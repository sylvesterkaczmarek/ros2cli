# Copyright 2026 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import patch

from ros2interface.verb.show import _show_interface


def test_show_interface_prints_original_idl(tmp_path, capsys):
    idl_text = (
        'module test_interfaces {\n'
        '  module msg {\n'
        '    struct Example {\n'
        '      long value;\n'
        '    };\n'
        '  };\n'
        '};\n'
    )
    idl_path = tmp_path / 'Example.idl'
    idl_path.write_text(idl_text, encoding='utf-8')

    with patch(
        'ros2interface.verb.show.get_interface_path',
        return_value=str(idl_path),
    ), patch('ros2interface.verb.show._get_interface_lines') as get_lines:
        _show_interface('test_interfaces/msg/Example')

    assert capsys.readouterr().out == idl_text
    get_lines.assert_not_called()
