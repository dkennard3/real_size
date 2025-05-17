from optparse import OptionParser
def arg_processor():
    parser = OptionParser(usage="usage: realsize.py [options] filepath")
    parser.add_option("-s", "--no-show-hidden", dest="show_hidden",
                      action="store_false", default=True,
                      help="exclude dot-files and hidden files from all summation counts")
    parser.add_option("-n", type="int", default=100000,
                      dest="max_depth", help="how many subdirectories 'deep' you wish to see starting from the given filepath. If unspecified, all subdirectories (and their subdirectories, recursively) are included")
    parser.add_option("-b", "--use_binary",
                      action="store_true", dest="use_binary", default=False,
                      help="use binary units [\"KiB\",\"MiB\",\"GiB\"] with byte value totals, "
                      "where each unit is factored by 2^10 (or 1,024); "
                      "otherwise, decimal units [\"kB\",\"MB\",\"GB\"] are used by default, "
                      "where each unit is factored by 10^3 (or 1,000)")
    parser.add_option("-c", "--count_only",
                      action="store_true", dest="show_count_only", default=False,
                      help="when set, only show folder, file, and byte counts")
    return parser
