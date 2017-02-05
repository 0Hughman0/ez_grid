import unittest
from datetime import date, timedelta

from ez_grid import Grid, Cell


class BaseCase:

    def compare_cells(self, got, expected):
        t_grid = Grid.from_lines(expected)
        for cell, t_cell in zip(got.cells, t_grid.cells):
            self.assertEqual(cell.row, t_cell.row)
            self.assertEqual(cell.col, t_cell.col)
            self.assertEqual(cell.value, t_cell.value)

    def test_headings(self):
        self.assertSequenceEqual(self.grid.row_hds, ("Row 1", "Row 2"))
        self.assertSequenceEqual(self.grid.col_hds, ("Col 1", "Col 2", "Col 3", "Col 4"))

    def test_subscripting(self):
        self.assertEqual(self.grid["Row 1"]["Col 3"], 3)
        self.assertEqual(self.grid["Row 2"]["Col 2"], 6)
        self.assertEqual(self.grid["Row 2"]["Col 4"], 8)
        self.assertRaises(KeyError, lambda: self.grid["Row ?"])
        self.assertRaises(KeyError, lambda: self.grid["Row 1"]["Col ?"])

    def test_iters(self):

        cols_tuple = ((1, 5),
                      (2, 6),
                      (3, 7),
                      (4, 8))
        for col, t_col in zip(self.grid.cols, cols_tuple):
            for value, t_value in zip(col, t_col):
                self.assertEqual(value, t_value)

        rows_tuple = ((1, 2, 3, 4),
                      (5, 6, 7, 8))
        for row, t_row in zip(self.grid.rows, rows_tuple):
            for value, t_value in zip(row, t_row):
                self.assertEqual(value, t_value)

        expected = \
            (("Row 1", "Col 1", 1), ("Row 1", "Col 2", 2), ("Row 1", "Col 3", 3), ("Row 1", "Col 4", 4),
             ("Row 2", "Col 1", 5), ("Row 2", "Col 2", 6), ("Row 2", "Col 3", 7), ("Row 2", "Col 4", 8))
        iter_expected = iter(expected)
        for row_hd, row in zip(self.grid.row_hds, self.grid.rows):
            for col_hd, value in zip(self.grid.col_hds, row):
                t_row_hd, t_col_hd, t_value = iter_expected.__next__()
                self.assertEqual(row_hd, t_row_hd)
                self.assertEqual(col_hd, t_col_hd)
                self.assertEqual(value, t_value)
        cells_tuple = []
        for row_hd, col_hd, value in expected:
            cells_tuple.append(Cell(row_hd, col_hd, value))
        for cell, t_cell in zip(self.grid.cells, cells_tuple):
            self.assertEqual(cell, t_cell)


    def test_col_row(self):
        self.assertSequenceEqual(tuple(self.grid.col("Col 1")), (1, 5))
        self.assertSequenceEqual(tuple(self.grid.col("Col 4")), (4, 8))
        self.assertSequenceEqual(tuple(self.grid.col("Col 3")), (3, 7))
        self.assertSequenceEqual(tuple(self.grid.row("Row 1")), (1, 2, 3, 4))
        self.assertSequenceEqual(tuple(self.grid.row("Row 2")), (5, 6, 7, 8))
        self.assertRaises(KeyError, lambda: self.grid.col("Col ?").__next__()) # __next__() needed as error is raised at iteration
        self.assertRaises(KeyError, lambda: self.grid.row("Row ?").__next__())

    def test_appends(self):
        self.grid.append_row("Row 3", (9, 10, 11, 12))
        expected = \
            (("Test Grid", "Col 1", "Col 2", "Col 3", "Col 4"),
             (    "Row 1",       1,       2,       3,       4),
             (    "Row 2",       5,       6,       7,       8),
             (    "Row 3",       9,      10,      11,      12))
        self.compare_cells(self.grid, expected)
        self.assertRaises(IndexError, self.grid.append_row, "Row 4", (1, 2, 3, 4, 5))
        self.assertRaises(ValueError, self.grid.append_row, "Row 1", (9, 10, 11, 12))
        self.grid.append_col("Col 5", (1, 2, 3))
        expected = \
            (("Test Grid", "Col 1", "Col 2", "Col 3", "Col 4", "Col 5"),
             (    "Row 1",       1,       2,       3,       4,       1),
             (    "Row 2",       5,       6,       7,       8,       2),
             (    "Row 3",       9,      10,      11,      12,       3))
        self.compare_cells(self.grid, expected)
        self.assertRaises(IndexError, self.grid.append_col, "Col 6", (1, 2, 3, 4))
        self.assertRaises(ValueError, self.grid.append_col, "Col 1", (9, 10, 11))

    def test_sets(self):
        self.grid.set_row("Row 1", ("new 1", "new 2", "new 3", "new 4"))
        expected = \
            (("Test Grid", "Col 1", "Col 2", "Col 3", "Col 4"),
             (    "Row 1", "new 1", "new 2", "new 3", "new 4"),
             (    "Row 2",       5,       6,       7,       8))
        self.compare_cells(self.grid, expected)
        self.assertRaises(KeyError, self.grid.set_row, "Row ?", ("new 1", "new 2", "new 3", "new 4"))
        self.assertRaises(IndexError, self.grid.set_row, "Row 1", ("new 1", "new 2", "new 3", "new 4", "new 5"))
        self.grid.set_col("Col 2", ("new 9", "new 10"))
        expected = \
            (("Test Grid", "Col 1", "Col 2", "Col 3", "Col 4"),
             (    "Row 1", "new 1", "new 9", "new 3", "new 4"),
             (    "Row 2",       5,"new 10",       7,       8))
        self.compare_cells(self.grid, expected)
        self.assertRaises(KeyError, self.grid.set_col, "Col ?", ("new 9", "new 10"))
        self.assertRaises(IndexError, self.grid.set_col, "Col 2", ("new 9", "new 10", "new 11"))

    def test_combine_all_new(self):
        to_combine = \
            (("Combine Grid", "Col 5", "Col 6", "Col 7", "Col 8"),
             (       "Row 1",       9,      10,      11,      12),
             (       "Row 2",      13,      14,      15,      16))
        expected = \
            (("Test Grid", "Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col 6", "Col 7", "Col 8"),
             (    "Row 1",       1,       2,       3,       4,       9,      10,      11,      12),
             (    "Row 2",       5,       6,       7,       8,      13,      14,       15,     16))
        new_grid = Grid.from_lines(to_combine)
        self.grid.combine(new_grid)
        self.compare_cells(self.grid, expected)

    def test_combine_overlap(self):
        to_combine = \
            (("Combine Grid", "Col 2", "Col 5",  "Col 6",  "Col 8"),
             (       "Row 1",      13,      14,       15,       16),
             (       "Row 2",       9,      10,       11,       12))
        expected = \
            (("Test Grid", "Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col 6", "Col 8"),
             (    "Row 1",       1,      13,       3,       4,       14,      15,     16),
             (    "Row 2",       5,      9,       7,       8,       10,      11,      12))
        new_grid = Grid.from_lines(to_combine)
        self.grid.combine(new_grid)
        self.compare_cells(self.grid, expected)

    def test_combine_overlap_ow_false(self):
        to_combine = \
            (("Combine Grid", "Col 2", "Col 5",  "Col 6",  "Col 8"),
             (       "Row 1",      13,      14,       15,       16),
             (       "Row 2",       9,      10,       11,       12))
        expected = \
            (("Test Grid", "Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col 6", "Col 8"),
             (    "Row 1",       1,      2,       3,       4,       14,      15,      16),
             (    "Row 2",       5,      6,       7,       8,       10,      11,      12))
        new_grid = Grid.from_lines(to_combine)
        self.grid.combine(new_grid, False)
        self.compare_cells(self.grid, expected)

    def test_swaps(self):
        self.grid.swap_rows("Row 1", "Row 2")
        self.grid.swap_cols("Col 4", "Col 2")
        expected = \
            (("Test Grid", "Col 1", "Col 4", "Col 3", "Col 2"),
             (    "Row 2",       5,       8,       7,       6),
             (    "Row 1",       1,       4,       3,       2))
        self.compare_cells(self.grid, expected)

    def test_writing(self):
        with open("tests/t_out.csv", "w") as file:
            self.grid.save_to_file(file)
        with open("tests/t_out.csv", "r") as file:
            written_grid = Grid.from_csv_file(file)
        expected = \
            (("Test Grid", "Col 1", "Col 2", "Col 3", "Col 4"),
             (    "Row 1",     "1",     "2",     "3",     "4"),
             (    "Row 2",     "5",     "6",     "7",     "8"))
        self.compare_cells(written_grid, expected)


class FromLinesCase(unittest.TestCase, BaseCase):

    def setUp(self):
        self.input = (("Test Grid", "Col 1", "Col 2", "Col 3", "Col 4"),
                      (    "Row 1",       1,       2,       3,       4),
                      (    "Row 2",       5,       6,       7,       8))
        self.grid = Grid.from_lines(self.input)


class FromCsvCase(unittest.TestCase, BaseCase):

    class IntGrid(Grid):

        def preprocess_value(self, row, col, value):
            return int(value)

    def setUp(self):
        with open(r"tests/test_grid.csv", "r") as file:
            self.grid = self.IntGrid.from_csv_file(file)


class FilledCase(unittest.TestCase, BaseCase):

    def setUp(self):
        filled_grid = Grid(("Row 1", "Row 2"),
                           ("Col 1", "Col 2", "Col 3", "Col 4"),
                                 "Test Grid")
        for row in range(1, 3):
            for col in range(1, 5):
                filled_grid["Row {}".format(row)]["Col {}".format(col)] = ((row - 1) * 4) + col
        self.grid = filled_grid


class NonStringHeadingsCase(unittest.TestCase):

    def setUp(self):
        self.grid = Grid(list(range(5)), (date(1994, 2, 5) + timedelta(days=d) for d in range(3)), default="sdf")

    def test_repr(self):
        expected = ("   1994-02-05  1994-02-06  1994-02-07  \n"
                    "0  sdf         sdf         sdf         \n"
                    "1  sdf         sdf         sdf         \n"
                    "2  sdf         sdf         sdf         \n"
                    "3  sdf         sdf         sdf         \n"
                    "4  sdf         sdf         sdf         ")
        self.assertEquals(str(self.grid), expected)


if __name__ == "__main__":
    unittest.main()


