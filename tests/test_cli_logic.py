import pytest
import sys
from unittest.mock import patch, MagicMock

# IMPORTANT: Change the import below to match your script name (aptUpdater)
from aptUpdater import run_update, get_scan_options 

# ----------------------------------------------------------------------
# SETUP MOCKS & HELPERS
# ----------------------------------------------------------------------

def mock_process(returncode, stdout_lines, stderr_output=""):
    """Creates a mock subprocess object that simulates a running process."""
    mock_proc = MagicMock()
    mock_proc.returncode = returncode
    
    # Mock the stdout stream to return lines one by one until empty
    mock_proc.stdout.readline.side_effect = stdout_lines + [""]
    mock_proc.stdout.read.return_value = "".join(stdout_lines)
    
    # Mock the stderr stream
    mock_proc.stderr.read.return_value = stderr_output
    
    # Mock the poll() method to indicate process is done after lines are read
    # We add enough 'None' calls to cover all readline calls, then the final returncode
    mock_proc.poll.side_effect = [None] * (len(stdout_lines) + 1) + [returncode]
    mock_proc.wait.return_value = None
    
    return mock_proc

# ----------------------------------------------------------------------
# TEST SUITE
# ----------------------------------------------------------------------

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
    
    # Check if the error code message was printed
    captured = capsys.readouterr()
    assert "Process finished with error code: 100" in captured.out
    

@patch('aptUpdater.subprocess.Popen')
def test_dry_run_flag_is_not_added(mock_popen, capsys):
    """
    Tests the dry run command (Option 5), ensuring:
    1. The progress flag is NOT added.
    2. The special "Dry run complete" message is printed.
    """
    
    # Mock output lines for the dry-run simulation
    mock_stdout = [
        "The following packages would be upgraded:",
        "  package-A package-B",
    ]
    
    # Set the mock to return a successful process
    mock_popen.return_value = mock_process(0, mock_stdout)
    
    # Command for dry run (Option 5)
    command = get_scan_options(5)
    
    # Execute the function, explicitly setting dry_run=True
    result_code = run_update(command, dry_run=True)
    
    # Assertions
    assert result_code == 0
    
    # Check if Popen was called: The command should be ['sudo', 'apt-get', 'upgrade', '--dry-run']
    call_args, _ = mock_popen.call_args
    command_used = call_args[0]
    
    # Assert the progress flag is NOT in the command list
    assert '-o' not in command_used
    
    # Assert the specific dry run message was printed
    captured = capsys.readouterr()
    assert "Dry run complete. No changes were made." in captured.out
