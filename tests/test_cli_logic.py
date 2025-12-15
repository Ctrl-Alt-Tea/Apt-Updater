import pytest
from unittest.mock import patch, MagicMock
from aptUpdater import run_update, get_scan_options

# ──────────────────────────────────────────────
# Helper Mock Class (Essential for Popen testing)
# ──────────────────────────────────────────────

class MockProcess:
    """Mock subprocess.Popen object for testing."""
    def __init__(self, returncode, stdout_lines, stderr_output=None):
        self.returncode = returncode
        self.stdout_lines = stdout_lines
        self.stderr_output = stderr_output
        self.stdout = self
        self.read_index = 0

    def readline(self):
        """Simulates reading one line from stdout pipe."""
        if self.read_index < len(self.stdout_lines):
            line = self.stdout_lines[self.read_index] + '\n'
            self.read_index += 1
            return line
        return ''

    def poll(self):
        """Simulates checking if the process is finished."""
        if self.read_index >= len(self.stdout_lines):
            return self.returncode
        return None

    def close(self):
        """Mock close method for stdout pipe."""
        pass

# Helper to create a process mock instance
def mock_process(returncode, stdout_lines, stderr_output=None):
    return MockProcess(returncode, stdout_lines, stderr_output)


# ──────────────────────────────────────────────
# Test Cases
# ──────────────────────────────────────────────

@patch('aptUpdater.subprocess.Popen')
def test_successful_upgrade_captures_packages_and_progress(mock_popen, capsys):
    """
    Tests a successful upgrade (Option 2), ensuring:
    1. Return code is 0.
    2. Progress flag is used.
    3. Package names are captured for the summary.
    """

    # Mock output lines simulating a successful upgrade with progress updates
    mock_stdout = [
        "dlstatus:10.0:Downloading packageA",
        "Inst package-A (1.0-1ubuntu1)",
        "dlstatus:50.0:Downloading packageB",
        "Inst package-B (2.0-1ubuntu1)",
        "pmstatus:80.0:Unpacking package-A",
        "pmstatus:100.0:Setting up package-B",
    ]

    # Set the mock to return a successful process (returncode 0)
    mock_popen.return_value = mock_process(0, mock_stdout)

    # Command for upgrade (Option 2)
    command = get_scan_options(2)

    # Execute the function
    result_code = run_update(command)

    # Assertions
    assert result_code == 0

    # 1. Check if Popen was called with the correct flags
    # The command should end with: ['-o', 'APT::Status-Fd=1']
    call_args, _ = mock_popen.call_args
    assert call_args[0][-1] == 'APT::Status-Fd=1'

    # 2. Check if the summary was printed with the correct package names
    captured = capsys.readouterr()
    assert "package-A" in captured.out
    assert "package-B" in captured.out
    # Check for the key part of the summary message
    assert "Upgrade Summary" in captured.out


@patch('aptUpdater.subprocess.Popen')
def test_failed_command_returns_non_zero(mock_popen, capsys):
    """
    Tests that a failed command (e.g., Option 1: update) returns a non-zero code
    and prints the error message.
    """

    # Mock output: The process fails after reading the update lines
    mock_stdout = [
        "Hit:1 http://repo.com/ubuntu focal InRelease",
        "Error line 1",
    ]

    # Set the mock to return a failed process (exit code 100)
    mock_popen.return_value = mock_process(100, mock_stdout, stderr_output="Critical dependency error.")

    # Command for update (Option 1)
    command = get_scan_options(1)

    # Execute the function
    result_code = run_update(command)

    # Assertions
    assert result_code == 100

    # Check if the error code message was printed, including the leading newline
    assert "\n\n" in captured.out  # Check for the double newline
    assert "Process finished with error code: 100" in captured.out

@patch('aptUpdater.subprocess.Popen')
def test_dry_run_flag_is_not_added(mock_popen, capsys):
    """
    Tests the dry run command (Option 4), ensuring:
    1. The progress flag is NOT added.
    2. The special "Dry run complete" message is printed.
    3. Returns a successful exit code (0).
    """

    # Mock output lines for the dry-run simulation
    mock_stdout = [
        "The following packages would be upgraded:",
        "  package-A package-B",
    ]

    # Set the mock to return a successful process
    mock_popen.return_value = mock_process(0, mock_stdout)

    # Command for dry run (Option 4, previously Option 5)
    command = get_scan_options(4)

    # Execute the function, explicitly setting dry_run=True
    result_code = run_update(command, dry_run=True)

    # Assertions
    captured = capsys.readouterr()

    # 1. Check for the final success message (includes newline)
    assert "\n\n" in captured.out  # Check for the double newline
    assert "Dry run complete. No changes were made." in captured.out
    
    # 2. Check Popen was called without the status flag
    call_args, _ = mock_popen.call_args
    assert '-o' not in call_args[0]
    
    # 3. Assert the result code is 0
    assert result_code == 0


@patch('aptUpdater.subprocess.Popen')
def test_search_command_prints_output_and_success(mock_popen, capsys):
    """
    Tests the search command (new Option 5), ensuring:
    1. The correct search command is used.
    2. The raw output is printed.
    3. The final 'Search complete' message is printed.
    """

    # Mock output lines for search
    mock_stdout = [
        "package-search-a - description for package A",
        "package-search-b - description for package B",
    ]

    # Set the mock to return a successful process
    mock_popen.return_value = mock_process(0, mock_stdout)

    # Command for search (Option 5)
    command = get_scan_options(5) + ["test-search"]

    # Execute the function, explicitly setting is_search=True
    result_code = run_update(command, is_search=True)

    # Assertions
    assert result_code == 0

    # 1. Check if Popen was called with the correct command (apt-cache search test-search)
    call_args, _ = mock_popen.call_args
    assert call_args[0] == ["sudo", "apt-cache", "search", "test-search"]

    # 2. Check if the output and success message were printed
    captured = capsys.readouterr()
    assert "package-search-a - description for package A" in captured.out
    assert "package-search-b - description for package B" in captured.out
    
    # Check for the final success message
    assert "Search complete." in captured.out
