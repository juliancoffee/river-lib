from river.parser.parse import (
    tokenize,
    LambdaLeaf,
    SequenceGroup,
    SetGroup,
    Assignment,
)


class TestLambda:
    def test_id(self):
        assert tokenize("x: x") == LambdaLeaf('x', 'x')


class TestLine:
    def test_plain(self):
        assert tokenize("[4, 5]") == SequenceGroup(['4', '5'])

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
                        Assignment('x', '5'),
                        Assignment('y', SequenceGroup(['4', '5']))
                    ]
                )
            ]
        )
        assert tokenize(src) == expected


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
                Assignment('a', '5'),
                Assignment('b', '6'),
            ]
        )
        assert tokenize(src) == expected

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
                    Assignment('x', '5'),
                    Assignment('y', '6'), ])
                ),
                Assignment('b', SetGroup([
                    Assignment('z', '7'),
                    Assignment('t', '8'), ]))
            ])
        assert tokenize(src) == expected
