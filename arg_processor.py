from optparse import OptionParser
def arg_processor():
    parser = OptionParser(usage="usage: realsize.py [options] filepath")
    parser.add_option("-n", type="int", default=100000,
                      dest="max_depth", help="how many subdirectories 'deep' you wish to see starting from the given filepath. If unspecified, all subdirectories (and their subdirectories, recursively) are included")
    parser.add_option("-d", "--use_decimal",
                      action="store_true", dest="use_decimal", default=False,
                      help="use decimal units [\"kB\",\"MB\",\"GB\"] with byte value totals, "
                      "where each unit is factored by 10^3 (or 1,000); "
                      "otherwise, binary units [\"KiB\",\"MiB\",\"GiB\"] are used by default, "
                      "and each unit is factored by 2^10 (or 1,024)")
    return parser
