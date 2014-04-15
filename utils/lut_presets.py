""" LUT preset
    A preset is a dict containing LUT parameters.
    The dict must have these attributes:
    {
    'type': <'default' or '1D' or '2D' or '3D'>,
    'extension': <str value>,
    'input_range': <[int/float, int/float]>,
    'output_range': <[int/float, int/float]>,
    'output_bitdepth': <int value>,
    'cube_size': <int value>,
    'title': <str value>,
    'comment': <str value>,
    'version': <str value>
    }
    See attribute constant below.

    When 1D or 2D type is chosen, preset must define output_bitdepth but
    shouldn't define cube_size.

    When 3D is chosen, preset must define cube_size but shouldn't define
    output_bitdepth.

    'default' is used to declare default sets, it must define both
    output_bitdepth and cube_size

.. moduleauthor:: `Marie FETIVEAU <github.com/mfe>`_

"""
__version__ = "0.1"
import collections


class PresetException(Exception):
    """Module custom exception

    """
    pass

# Attributes
TYPE = 'type'
TYPE_CHOICE = ['default', '1D', '2D', '3D']
EXT = 'extension'
VERSION = 'version'
TITLE = 'title'
COMMENT = 'comment'
IN_RANGE = 'input_range'
OUT_RANGE = 'output_range'

# 1D / 2D specific attribute
OUT_BITDEPTH = 'output_bitdepth'

# 3D specific attribute
CUBE_SIZE = 'cube_size'

BASIC_ATTRS = [TYPE, EXT, VERSION, TITLE, COMMENT, IN_RANGE, OUT_RANGE]

BITDEPTH_MAX_VALUE = 128
BITDEPTH_MIN_VALUE = 8
CUBE_SIZE_MAX_VALUE = 128
CUBE_SIZE_MIN_VALUE = 3


def get_default_preset():
    """ Get a general default preset.
        Values were chosen considering common LUT use cases.

    """
    return {
                TYPE: "default",
                EXT: ".lut",
                IN_RANGE: [0.0, 1.0],
                OUT_RANGE: [0.0, 1.0],
                OUT_BITDEPTH: 12,
                CUBE_SIZE: 17,
                TITLE: "LUT",
                COMMENT: ("Generated by ColorPipe-tools"
                            ).format(__version__),
                VERSION: "1"
           }


def __is_range(arange):
    """ Return True if range is a collection composed of 2 int or float

    """
    if not isinstance(arange, collections.Iterable):
        return False
    if len(arange) != 2:
        return False
    for value in arange:
        if not isinstance(value, (int, float)):
            return False
    return True


RAISE_MODE = 'raise'
FILL_MODE = 'fill'


def __validate_preset(preset, mode=RAISE_MODE):
    """ Check preset. When an irregularity is found, if mode is 'raise'
    an exception is thrown, else preset is completed with default values

    Args:
        preset (dict): preset to validate

    Kwargs:
        mode (str): raise or fill. Default is raise.

    """
    # check if basic attribute are present
    missing_attr_msg = "Preset must have '{0}' attribute"
    default_preset = get_default_preset()
    for attr in BASIC_ATTRS:
        if attr not in preset:
            if mode == RAISE_MODE:
                raise PresetException(missing_attr_msg.format(attr))
            preset[attr] = default_preset[attr]
    # check if type is correct
    if not preset[TYPE] in TYPE_CHOICE:
        if mode == RAISE_MODE:
            raise PresetException(("{0} is not a valid type: "
                                  "{1}").format(preset[TYPE], TYPE_CHOICE))
        preset[TYPE] = default_preset[TYPE]
    ## check if type specific attr are set
    # default type
    if preset[TYPE] == 'default' and (OUT_BITDEPTH not in preset
                                      or CUBE_SIZE not in preset):
        if mode == RAISE_MODE:
            raise PresetException(("A default preset must define '{0} and "
                                   "'{1}' attributes").format(OUT_BITDEPTH,
                                                              CUBE_SIZE))
        if OUT_BITDEPTH not in preset:
            preset[OUT_BITDEPTH] = default_preset[OUT_BITDEPTH]
        if CUBE_SIZE not in preset:
            preset[CUBE_SIZE] = default_preset[CUBE_SIZE]
        preset[TYPE] = default_preset[TYPE]
    # 1D / 2D type
    if preset[TYPE] == '1D' or preset[TYPE] == '2D':
        if OUT_BITDEPTH not in preset:
            if mode == RAISE_MODE:
                raise PresetException(("A 1D/2D preset must define '{0}"
                                       "attribute").format(OUT_BITDEPTH))
            preset[OUT_BITDEPTH] = default_preset[OUT_BITDEPTH]
        elif (not isinstance(preset[OUT_BITDEPTH], int)
              or preset[OUT_BITDEPTH] < BITDEPTH_MIN_VALUE
              or preset[OUT_BITDEPTH] > BITDEPTH_MAX_VALUE):
            if mode == RAISE_MODE:
                raise PresetException(("Invalid bit depth: {0}"
                                       ).format(preset[OUT_BITDEPTH]))
            preset[OUT_BITDEPTH] = default_preset[OUT_BITDEPTH]
    # 3D type
    if preset[TYPE] == '3D':
        if CUBE_SIZE not in preset:
            if mode == RAISE_MODE:
                raise PresetException(("A 3D preset must define '{0}"
                                       "attribute").format(CUBE_SIZE))
            preset[CUBE_SIZE] = default_preset[CUBE_SIZE]
        elif (not isinstance(preset[CUBE_SIZE], int)
              or preset[CUBE_SIZE] < CUBE_SIZE_MIN_VALUE
              or preset[CUBE_SIZE] > CUBE_SIZE_MAX_VALUE):
            if mode == RAISE_MODE:
                raise PresetException(("Invalid cube size: {0}"
                                       ).format(preset[CUBE_SIZE]))
            preset[CUBE_SIZE] = default_preset[CUBE_SIZE]
    # Check ranges
    ranges = IN_RANGE, OUT_RANGE
    for arange in ranges:
        if not __is_range(preset[arange]):
            if mode == RAISE_MODE:
                raise PresetException(("Invalid range: {0}"
                                       ).format(preset[arange]))
            preset[arange] = default_preset[arange]
    # return updated preset
    return preset


def check_preset(preset):
    """ Check preset. When an irregularity is found, an exception is thrown

    Args:
        preset (dict): preset to validate

    """
    __validate_preset(preset, RAISE_MODE)


def complete_preset(preset):
    """ Check preset. When an irregularity is found, preset is completed with
    default values

    Args:
        preset (dict): preset to validate

    """
    __validate_preset(preset, FILL_MODE)


def is_3d_preset(preset):
    """ Check if preset is valid for 3D LUTs
        Should be used after a check or complete

    """
    if preset[TYPE] == 'default' or preset[TYPE] == '3D':
        return True
    return False


def is_1d_or_2d_preset(preset):
    """ Check if preset is valid for 1D / 2D LUTs
        Should be used after a check or complete

    """
    if (preset[TYPE] == 'default'
        or preset[TYPE] == '1D'
        or preset[TYPE] == '2D'):
        return True
    return False
