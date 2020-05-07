from river.parser.parse import lexer

from river.parser.groups import (
    LambdaLeaf,
    SequenceGroup,
    SetGroup,
    Assignment,
)

from river.parser.tokenize import Text

# TODO: Add more unit tests on grouping, group_parts, and so on


class TestLambda:
    def test_id(self):
        assert lexer("x: x") == LambdaLeaf('x', Text('x'))


class TestLine:
    def test_plain(self):
        assert lexer("[4, 5]") == SequenceGroup([Text('4'), Text('5')])

    def test_one_set_with_line(self):
        src = """
        [
            {
                x = 5;
                y = [4, 5];
            }
        ]
        """
        expected = SequenceGroup(
            [
                SetGroup(
                    [
                        Assignment('x', Text('5')),
                        Assignment('y', SequenceGroup([Text('4'), Text('5')]))
                    ]
                )
            ]
        )
        assert lexer(src) == expected


class TestTable:
    def test_plain(self):
        src = """
        {
            a = 5;
            b = 6;
        }
        """
        expected = SetGroup(
            [
                Assignment('a', Text('5')),
                Assignment('b', Text('6')),
            ]
        )
        assert lexer(src) == expected

    def test_with_sets(self):
        src = """
        {
            a = {
                x = 5;
                y = 6;
            };
            b = {
                z = 7;
                t = 8;
            };
        }
        """
        expected = SetGroup(
            [
                Assignment('a', SetGroup([
                    Assignment('x', Text('5')),
                    Assignment('y', Text('6')), ])
                ),
                Assignment('b', SetGroup([
                    Assignment('z', Text('7')),
                    Assignment('t', Text('8')), ]))
            ])
        assert lexer(src) == expected
