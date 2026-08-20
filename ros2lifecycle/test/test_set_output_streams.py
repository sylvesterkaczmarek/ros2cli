# Copyright 2026 Sylvester Kaczmarek
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

from contextlib import redirect_stderr
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from ros2lifecycle.verb.set import SetVerb


class _ContextManager:

    def __init__(self, value):
        self._value = value

    def __enter__(self):
        return self._value

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def _run_set_verb(result):
    node_name = '/test_lifecycle_node'
    args = SimpleNamespace(
        node_name=node_name,
        include_hidden_nodes=False,
        transition='configure',
        timeout=None,
    )
    transition = SimpleNamespace(
        transition=SimpleNamespace(label='configure', id=1)
    )
    stdout = StringIO()
    stderr = StringIO()

    with patch(
        'ros2lifecycle.verb.set.NodeStrategy',
        return_value=_ContextManager(object())
    ), patch(
        'ros2lifecycle.verb.set.DirectNode',
        return_value=_ContextManager(object())
    ), patch(
        'ros2lifecycle.verb.set.get_node_names',
        return_value=[SimpleNamespace(full_name=node_name)]
    ), patch(
        'ros2lifecycle.verb.set.get_absolute_node_name',
        return_value=node_name
    ), patch(
        'ros2lifecycle.verb.set.call_get_available_transitions',
        return_value={node_name: [transition]}
    ), patch(
        'ros2lifecycle.verb.set.call_change_states',
        return_value={node_name: result}
    ), redirect_stdout(stdout), redirect_stderr(stderr):
        return_code = SetVerb().main(args=args)

    return return_code, stdout.getvalue(), stderr.getvalue()


def test_successful_transition_uses_stdout():
    return_code, stdout, stderr = _run_set_verb(True)

    assert return_code is None
    assert stdout == 'Transitioning successful\n'
    assert stderr == ''


def test_failed_transition_uses_stderr():
    return_code, stdout, stderr = _run_set_verb(False)

    assert return_code is None
    assert stdout == ''
    assert stderr == 'Transitioning failed\n'


def test_transition_exception_uses_stderr():
    return_code, stdout, stderr = _run_set_verb(RuntimeError('transition error'))

    assert return_code is None
    assert stdout == ''
    assert stderr == (
        "Exception while calling service of node '/test_lifecycle_node': transition error\n"
    )
