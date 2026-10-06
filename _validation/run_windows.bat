@echo off
call "%ROS_ROOT%\local_setup.bat"
if errorlevel 1 exit /b %errorlevel%
set "PYTHONPATH=%GITHUB_WORKSPACE%\ros2cli;%PYTHONPATH%"
set "ROS_DOMAIN_ID=57"
python -c "import os,sys,rclpy; import ros2cli.node.daemon as d; print(sys.version); print(os.name); print(d.__file__); print(rclpy.__file__)"
if errorlevel 1 exit /b %errorlevel%
python -m pytest -q -s "%GITHUB_WORKSPACE%\ros2cli\test\test_daemon_socket_acquisition.py" "%GITHUB_WORKSPACE%\_validation\test_windows_sockets.py" --junitxml="%GITHUB_WORKSPACE%\windows-results.xml"
exit /b %errorlevel%
