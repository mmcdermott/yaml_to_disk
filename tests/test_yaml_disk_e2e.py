import json

from yaml_to_disk import yaml_disk


def test_yaml_disk_end_to_end():
    yaml_data = {
        'sub/': {'a.txt': 'hello'},
        'b.json': {'foo': 'bar'},
    }
    with yaml_disk(yaml_data) as root:
        assert (root / 'sub' / 'a.txt').read_text() == 'hello'
        assert json.loads((root / 'b.json').read_text()) == {'foo': 'bar'}
    assert not root.exists()
