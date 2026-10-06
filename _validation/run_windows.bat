@echo off
call "%ROS_ROOT%\local_setup.bat"
if errorlevel 1 exit /b %errorlevel%
set "PYTHONPATH=%GITHUB_WORKSPACE%\ros2cli;%PYTHONPATH%"
set "ROS_DOMAIN_ID=57"
set "PYTHONDONTWRITEBYTECODE=1"
python -c "import os,sys,rclpy; import ros2cli.node.daemon as d; print(sys.version); print(os.name); print(d.__file__); print(rclpy.__file__)"
if errorlevel 1 exit /b %errorlevel%
python "%GITHUB_WORKSPACE%\_validation\compare_before_after.py"
exit /b %errorlevel%
