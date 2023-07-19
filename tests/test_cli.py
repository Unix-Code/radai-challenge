from main import handle_input_args


class TestCLIArgs:
    def test_help_flag(self, mocker):
        mock_print = mocker.patch("builtins.print")
        mock_sys_exit = mocker.patch("sys.exit")
        mock_sys_argv = mocker.patch("sys.argv", ["arbitrary", "--help"])
        handle_input_args()

        mock_print.assert_called_once_with(
            "Usage:\n<file_path> (Input File to use as input)\n<No Args> (Use STDIN as input)\n"
        )
        mock_sys_exit.assert_called_once_with()

    def test_no_args(self, mocker):
        mocker.patch("sys.argv", ["arbitrary"])
        assert handle_input_args() is None

    def test_too_many_args(self, mocker):
        mocker.patch("sys.argv", ["arbitrary", "test.txt", "wrong_additional_arg"])
        mock_sys_exit = mocker.patch("sys.exit")

        handle_input_args()

        mock_sys_exit.assert_called_once_with(
            "Invalid: Only 1 argument consisting of a file path is allowed.\n"
        )
