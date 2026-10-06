"""Run matching real-Windows regression cases before and after the patch."""
from pathlib import Path
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

root = Path(os.environ['GITHUB_WORKSPACE'])
source = root / 'ros2cli/ros2cli/node/daemon.py'
real_tests = root / 'ros2cli/test/test_daemon_socket_windows.py'
fixed = source.read_bytes()
baseline = subprocess.check_output([
    'git', 'show',
    'e2f917b44516d1153ebd1bc7c31ea99962d3af3b:ros2cli/ros2cli/node/daemon.py'
], cwd=root)
try:
    source.write_bytes(baseline)
    before_xml = root / 'windows-before.xml'
    before = subprocess.run([
        sys.executable, '-m', 'pytest', '-q', '-s', str(real_tests),
        '-k', 'foreign_bound_socket_is_bounded or nonresponsive_listening_socket_is_bounded',
        '--junitxml=' + str(before_xml)
    ], check=False, timeout=60)
    report = ET.parse(before_xml).getroot()
    cases = report.findall('.//testcase')
    assert before.returncode == 1, before.returncode
    assert len(cases) == 2 and all(c.find('failure') is not None for c in cases)
    print('CONFIRMED: both real-Windows timeout regressions fail before the fix.', flush=True)
finally:
    source.write_bytes(fixed)
after = subprocess.run([
    sys.executable, '-m', 'pytest', '-q', '-s',
    str(root / 'ros2cli/test/test_daemon_socket_acquisition.py'), str(real_tests),
    '--junitxml=' + str(root / 'windows-results.xml')
], check=False, timeout=120)
sys.exit(after.returncode)
