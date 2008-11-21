###############################################################################
# nvctrl.py: nvidia NV-CONTROL X extension functions in python
# this file contains only a subset of the NV-CONTROL functions,
# namely those for attribute information.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
        
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License at http://www.gnu.org/licenses/gpl.txt
# By using, editing and/or distributing this software you agree to
# the terms and conditions of this license.

import minx

###############################################################################
# NV-CONTROL integer attributes. this list contains constants defined in both
# NVCtrl.h and NVCtrlAttributes.h. these constants are the attribute codes
#
NV_CTRL_TARGET_TYPE_X_SCREEN = 0
NV_CTRL_TARGET_TYPE_GPU = 1
NV_CTRL_TARGET_TYPE_FRAMELOCK = 2
NV_CTRL_TARGET_TYPE_VCSC = 3

NV_CTRL_BUS_TYPE                        = 5   #/* R--G */
NV_CTRL_VIDEO_RAM                       = 6   #/* R--G */
NV_CTRL_IRQ                             = 7   #/* R--G */
NV_CTRL_OPERATING_SYSTEM                = 8   #/* R--G */
NV_CTRL_CONNECTED_DISPLAYS              = 19  #/* R--G */
NV_CTRL_ENABLED_DISPLAYS                = 20  #/* R--G */
NV_CTRL_FRAMELOCK                       = 21  #/* R--G */
NV_CTRL_ARCHITECTURE                    = 41  #/* R--- */
NV_CTRL_CURSOR_SHADOW                   = 43  #/* RW-- */
NV_CTRL_GPU_CORE_TEMPERATURE            = 60  #/* R--G */
NV_CTRL_GPU_CORE_THRESHOLD              = 61  #/* R--G */
NV_CTRL_GPU_DEFAULT_CORE_THRESHOLD      = 62  #/* R--G */
NV_CTRL_GPU_MAX_CORE_THRESHOLD          = 63  #/* R--G */
NV_CTRL_AMBIENT_TEMPERATURE             = 64  #/* R--G */
NV_CTRL_GVO_SUPPORTED                   = 67  #/* R--- */
NV_CTRL_GPU_2D_CLOCK_FREQS              = 89  #/* RW-G */
NV_CTRL_GPU_3D_CLOCK_FREQS              = 90  #/* RW-G */
NV_CTRL_GPU_DEFAULT_2D_CLOCK_FREQS      = 91  #/* R--G */
NV_CTRL_GPU_DEFAULT_3D_CLOCK_FREQS      = 92  #/* R--G */
NV_CTRL_GPU_CURRENT_CLOCK_FREQS         = 93  #/* R--G */
NV_CTRL_XINERAMA                        = 222 #/* R--G */
NV_CTRL_XINERAMA_STEREO                 = 223 #/* RW-- */
NV_CTRL_BUS_RATE                        = 224 #/* R--G */
NV_CTRL_ASSOCIATED_DISPLAY_DEVICES      = 231 #/* RW-- */
NV_CTRL_PROBE_DISPLAYS                  = 234 #/* R--G */
NV_CTRL_REFRESH_RATE                    = 235 #/* R-DG */
NV_CTRL_PCI_BUS                         = 239 #/* R--G */
NV_CTRL_PCI_DEVICE                      = 240 #/* R--G */
NV_CTRL_PCI_FUNCTION                    = 241 #/* R--G */
NV_CTRL_MAX_SCREEN_WIDTH                = 243 #/* R--G */
NV_CTRL_MAX_SCREEN_HEIGHT               = 244 #/* R--G */
NV_CTRL_MAX_DISPLAYS                    = 245 #/* R--G */
NV_CTRL_MULTIGPU_DISPLAY_OWNER          = 247 #/* R--- */
NV_CTRL_GPU_SCALING                     = 248 #/* RWDG */
NV_CTRL_GPU_POWER_SOURCE                = 262 #/* R--G */

NV_CTRL_DEPTH_30_ALLOWED                = 279 #/* R--G */
NV_CTRL_LAST_ATTRIBUTE                  = NV_CTRL_DEPTH_30_ALLOWED

NV_CTRL_BINARY_DATA_EDID                = 0   #/* R-DG */
NV_CTRL_BINARY_DATA_MODELINES           = 1   #/* R-DG */
NV_CTRL_BINARY_DATA_METAMODES           = 2   #/* R-D- */
NV_CTRL_BINARY_DATA_XSCREENS_USING_GPU  = 3   #/* R-DG */
NV_CTRL_BINARY_DATA_GPUS_USED_BY_XSCREEN= 4   #/* R--- */
NV_CTRL_BINARY_DATA_GPUS_USING_FRAMELOCK= 5   #/* R-DF */
NV_CTRL_BINARY_DATA_DISPLAY_VIEWPORT    = 6   #/* R-DG */
NV_CTRL_BINARY_DATA_FRAMELOCKS_USED_BY_GPU=7  #/* R-DG */
NV_CTRL_BINARY_DATA_GPUS_USING_VCSC     = 8   #/* R-DV */
NV_CTRL_BINARY_DATA_VCSCS_USED_BY_GPU   = 9   #/* R-DG */

NV_CTRL_BINARY_DATA_LAST_ATTRIBUTE      = NV_CTRL_BINARY_DATA_VCSCS_USED_BY_GPU

###############################################################################
# extensions defined in NVCtrlAttributes.h
#
NV_CTRL_ATTR_BASE                       = NV_CTRL_LAST_ATTRIBUTE + 1
NV_CTRL_ATTR_EXT_BASE                   = (NV_CTRL_ATTR_BASE)
NV_CTRL_ATTR_EXT_NV_PRESENT             = (NV_CTRL_ATTR_EXT_BASE + 0)
NV_CTRL_ATTR_EXT_VM_PRESENT             = (NV_CTRL_ATTR_EXT_BASE + 1)
NV_CTRL_ATTR_EXT_XV_OVERLAY_PRESENT     = (NV_CTRL_ATTR_EXT_BASE + 2)
NV_CTRL_ATTR_EXT_XV_TEXTURE_PRESENT     = (NV_CTRL_ATTR_EXT_BASE + 3)
NV_CTRL_ATTR_EXT_XV_BLITTER_PRESENT     = (NV_CTRL_ATTR_EXT_BASE + 4)

NV_CTRL_ATTR_EXT_LAST_ATTRIBUTE         = (NV_CTRL_ATTR_EXT_XV_BLITTER_PRESENT)
NV_CTRL_ATTR_NV_BASE                    = (NV_CTRL_ATTR_EXT_LAST_ATTRIBUTE + 1)


###############################################################################
# NV-CONTROL string attributes. this list contains constants defined in both
# NVCtrl.h and NVCtrlAttributes.h. these constants are the attribute codes
# for use with the string functions
#
NV_CTRL_STRING_PRODUCT_NAME             = 0   #/* R--G */
NV_CTRL_STRING_VBIOS_VERSION            = 1   #/* R--G */
NV_CTRL_STRING_NVIDIA_DRIVER_VERSION    = 3   #/* R--G */
NV_CTRL_STRING_DISPLAY_DEVICE_NAME      = 4   #/* R-DG */
NV_CTRL_STRING_CURRENT_MODELINE         = 9   #/* R-DG */
NV_CTRL_STRING_ADD_MODELINE             = 10  #/* -WDG */
NV_CTRL_STRING_DELETE_MODELINE          = 11  #/* -WDG */
NV_CTRL_STRING_CURRENT_METAMODE         = 12  #/* R--- */
NV_CTRL_STRING_ADD_METAMODE             = 13  #/* -W-- */
NV_CTRL_STRING_DELETE_METAMODE          = 14  #/* -WD- */
NV_CTRL_STRING_MOVE_METAMODE            = 23  #/* -W-- */
NV_CTRL_STRING_VALID_HORIZ_SYNC_RANGES  = 24  #/* R-DG */
NV_CTRL_STRING_VERT_REFRESH_RANGES      = 25  #/* R-DG */
NV_CTRL_STRING_XINERAMA_SCREEN_INFO     = 26  #/* R--- */
NV_CTRL_STRING_TWINVIEW_XINERAMA_INFO_ORDER=27#/* RW-- */
NV_CTRL_STRING_SLI_MODE                 = 28  #/* R--- */
NV_CTRL_STRING_PERFORMANCE_MODES        = 29  #/* R--G */
NV_CTRL_STRING_LAST_ATTRIBUTE           = NV_CTRL_STRING_PERFORMANCE_MODES

NV_CTRL_STRING_OPERATION_ADD_METAMODE   = 0
NV_CTRL_STRING_OPERATION_GTF_MODELINE   = 1
NV_CTRL_STRING_OPERATION_CVT_MODELINE   = 2
NV_CTRL_STRING_OPERATION_BUILD_MODEPOOL = 3   # /* DG  */
NV_CTRL_STRING_OPERATION_LAST_ATTRIBUTE = NV_CTRL_STRING_OPERATION_BUILD_MODEPOOL


###############################################################################
# NV-CONTROL major op numbers. these constants identify the request type
#
X_nvCtrlQueryExtension                  = 0
X_nvCtrlQueryAttribute                  = 2
X_nvCtrlQueryStringAttribute            = 4
X_nvCtrlQueryValidAttributeValues       = 5
X_nvCtrlSetStringAttribute              = 9
X_nvCtrlSetAttributeAndGetStatus        = 19
X_nvCtrlQueryBinaryData                 = 20
X_nvCtrlQueryTargetCount                = 24
X_nvCtrlStringOperation                 = 25


###############################################################################
# various lists that go with attributes, but are handled more compactly
# this way. these lists are indexed by the possible values of their attributes
# and are explained in NVCtrl.h
#
__BUS_TYPES = ['AGP', 'PCI', 'PCI Express', 'Integrated']
__OS_TYPES = ['Linux', 'FreeBSD', 'SunOS']
__ARCH_TYPES = ['x86', 'x86-64', 'IA64']


ATTRIBUTE_TYPE_UNKNOWN              = 0
ATTRIBUTE_TYPE_INTEGER              = 1
ATTRIBUTE_TYPE_BITMASK              = 2
ATTRIBUTE_TYPE_BOOL                 = 3
ATTRIBUTE_TYPE_RANGE                = 4
ATTRIBUTE_TYPE_INT_BITS             = 5

ATTRIBUTE_TYPE_READ                 = 0x01
ATTRIBUTE_TYPE_WRITE                = 0x02
ATTRIBUTE_TYPE_DISPLAY              = 0x04
ATTRIBUTE_TYPE_GPU                  = 0x08
ATTRIBUTE_TYPE_FRAMELOCK            = 0x10
ATTRIBUTE_TYPE_X_SCREEN             = 0x20
ATTRIBUTE_TYPE_XINERAMA             = 0x40
ATTRIBUTE_TYPE_VCSC                 = 0x80




###############################################################################
# NV-CONTROL Query Extension
#
class NVCtrlQueryExtensionRequest:
    '''this class wraps the NV-CONTROL query request.
    it requires the major opcode of NV-CONTROL as a
    constructor arg. the opcode can be obtained with
    an XQueryExtension'''

    def __init__(self, nvmajor):
        self.encoding = minx.encode( minx.XData('CARD8',1,nvmajor),
        minx.XData('CARD8',1,X_nvCtrlQueryExtension),
        minx.XData('CARD16',1,1) )


class NVCtrlQueryExtensionReply:
    '''the reply to a NVCtrlQueryExtension request. returns
    the major and minor versions of the NV-CONTROL extension
    (if supported, of course)'''

    def __init__(self,encoding):
        xreply, ad = minx.decode( encoding,
        minx.XData('BYTE',1,'type'),
        minx.XData('PAD',1,'padb1'),
        minx.XData('CARD16',1,'sequence_number'),
        minx.XData('CARD32',1,'reply_length'),
        minx.XData('CARD16',1,'major'),
        minx.XData('CARD16',1,'minor'),
        minx.XData('CARD32',1,'padl4'),
        minx.XData('CARD32',1,'padl5'),
        minx.XData('CARD32',1,'padl6'),
        minx.XData('CARD32',1,'padl7'),
        minx.XData('CARD32',1,'padl8') )

        for n, v in xreply.iteritems():
            setattr( self, n, v )


###############################################################################
# NV-CONTROL Query Attribute
#
class NVCtrlQueryAttributeRequest:
    '''this class wraps the NV-CONTROL query attribute request.
    it requires the major opcode of NV-CONTROL, the display or gpu
    to query, what type of target (display or gpu), the display
    mask (if target is a display, mask can be obtained with
    GetConnectedDisplays or GetActiveDisplays, if gpu, not used),
    and identifier of the attribute to query as constructor args. it
    returns the value of an integer driver attribute. this
    one can raise Value Error and Match error. see NVCtrlLib.h'''

    def __init__(self,nvmajor,target_id,target_type,display_mask,attribute):
        self.encoding = minx.encode( minx.XData('CARD8',1,nvmajor),
        minx.XData('CARD8',1,X_nvCtrlQueryAttribute),
        minx.XData('CARD16',1,4),
        minx.XData('CARD16',1,target_id),
        minx.XData('CARD16',1,target_type),
        minx.XData('CARD32',1,display_mask),
        minx.XData('CARD32',1,attribute) )
        

class NVCtrlQueryAttributeReply:
    '''the reply to NVCtrlQueryAttribute request. returns
    the value and the flags, which describe whether attribute
    is read-only, etc. see NVCtrlLib.h'''

    def __init__(self,encoding):
        xreply, ad = minx.decode( encoding,
        minx.XData('BYTE',1,'type'),
        minx.XData('BYTE',1,'pad0'),
        minx.XData('CARD16',1,'sequence_number'),
        minx.XData('CARD32',1,'length'),
        minx.XData('CARD32',1,'flags'),
        minx.XData('INT32',1,'value'),
        minx.XData('CARD32',1,'pad4'),
        minx.XData('CARD32',1,'pad5'),
        minx.XData('CARD32',1,'pad6'),
        minx.XData('CARD32',1,'pad7') )

        for n, v in xreply.iteritems():
            setattr( self, n, v )


###############################################################################
# NV-CONTROL Set Attribute And Get Status
#
class NVCtrlSetAttributeAndGetStatusRequest:
    def __init__(self,nvmajor,screen,display_mask,attribute,value):
        self.encoding = minx.encode( minx.XData('CARD8',1,nvmajor),
        minx.XData('CARD8',1,X_nvCtrlSetAttributeAndGetStatus),
        minx.XData('CARD16',1,5),
        minx.XData('CARD32',1,screen),
        minx.XData('CARD32',1,display_mask),
        minx.XData('CARD32',1,attribute),
        minx.XData('INT32',1,value) )

class NVCtrlSetAttributeAndGetStatusReply:
    def __init__(self,encoding):
        xreply, ad = minx.decode( encoding,
        minx.XData('BYTE',1,'type'),
        minx.XData('BYTE',1,'pad0'),
        minx.XData('CARD16',1,'sequence_number'),
        minx.XData('CARD32',1,'length'),
        minx.XData('CARD32',1,'flags'),
        minx.XData('CARD32',1,'pad3'),
        minx.XData('CARD32',1,'pad4'),
        minx.XData('CARD32',1,'pad5'),
        minx.XData('CARD32',1,'pad6'),
        minx.XData('CARD32',1,'pad7') )

        for n, v in xreply.iteritems():
            setattr( self, n, v )



###############################################################################
# NV-CONTROL Query Target Count
#
class NVCtrlQueryTargetCountRequest:
    '''this class wraps the NV-CONTROL query target count
    request. it requires the major opcode of NV-CONTROL and the
    type of target to count as args. the target types are kind of
    explained in NVCtrl.h. this request will return a count of
    the gpu's on the system, for example, with target type 1'''

    def __init__(self, nvmajor, target):
        self.encoding = minx.encode( minx.XData('CARD8',1,nvmajor),
        minx.XData('CARD8',1,X_nvCtrlQueryTargetCount),
        minx.XData('CARD16',1,2),
        minx.XData('CARD32',1,target) )


class NVCtrlQueryTargetCountReply:
    '''the reply to a NVCtrlQueryTargetCount request. returns
    the count of the given target type. causes an X Value error
    if the target type does not exist at all, so check for errors
    if u query something that might not be there'''

    def __init__(self,encoding):
        xreply, ad = minx.decode( encoding,
        minx.XData('BYTE',1,'type'),
        minx.XData('PAD',1,'padb1'),
        minx.XData('CARD16',1,'sequence_number'),
        minx.XData('CARD32',1,'length'),
        minx.XData('CARD32',1,'count'),
        minx.XData('CARD32',1,'padl4'),
        minx.XData('CARD32',1,'padl5'),
        minx.XData('CARD32',1,'padl6'),
        minx.XData('CARD32',1,'padl7'),
        minx.XData('CARD32',1,'padl8') )

        for n, v in xreply.iteritems():
            setattr( self, n, v )


###############################################################################
# NV-CONTROL Query Binary Data
#
class NVCtrlQueryBinaryDataRequest:
    '''this class wraps the NV-CONTROL query binary data request.
    it requires the major opcode of NV-CONTROL, the display or gpu
    to query, what type of target (display or gpu), the display
    mask (if target is a display, mask can be obtained with
    GetConnectedDisplays or GetActiveDisplays, if gpu, not used),
    and identifier of the attribute to query as constructor args. it
    returns the value of an integer driver attribute. this
    one can raise Value Error and Match error. see NVCtrlLib.h'''

    def __init__(self,nvmajor,target_id,target_type,display_mask,attribute):
        self.encoding = minx.encode( minx.XData('CARD8',1,nvmajor),
        minx.XData('CARD8',1,X_nvCtrlQueryBinaryData),
        minx.XData('CARD16',1,4),
        minx.XData('CARD16',1,target_id),
        minx.XData('CARD16',1,target_type),
        minx.XData('CARD32',1,display_mask),
        minx.XData('CARD32',1,attribute) )
 

class NVCtrlQueryBinaryDataReply:
    '''the reply to a NVCtrlQueryBinaryData request. returns
    the count of the given target type. causes an X Value error
    if the target type does not exist at all, so check for errors
    if u query something that might not be there'''

    def __init__(self,encoding):
        xreply, ad = minx.decode( encoding,
        minx.XData('BYTE',1,'type'),
        minx.XData('PAD',1,'pad0'),
        minx.XData('CARD16',1,'sequence_number'),
        minx.XData('CARD32',1,'length'),
        minx.XData('CARD32',1,'flags'),
        minx.XData('CARD32',1,'n'),
        minx.XData('CARD32',1,'pad4'),
        minx.XData('CARD32',1,'pad5'),
        minx.XData('CARD32',1,'pad6'),
        minx.XData('CARD32',1,'pad7') )

        for n, v in xreply.iteritems():
            setattr( self, n, v )

        rs, ad = minx.decode( ad,
            minx.XData('STRING8',self.n,'data') )
        self.data = str(rs['data'])


###############################################################################
# NV-CONTROL Query String Attribute
#
class NVCtrlQueryStringAttributeRequest:
    '''this is the string version of Query Attribute. works
    just like the int version, only the reply is different'''

    def __init__(self,nvmajor,target_id,target_type,display_mask,attribute):
        self.encoding = minx.encode( minx.XData('CARD8',1,nvmajor),
        minx.XData('CARD8',1,X_nvCtrlQueryStringAttribute),
        minx.XData('CARD16',1,4),
        minx.XData('CARD16',1,target_id),
        minx.XData('CARD16',1,target_type),
        minx.XData('CARD32',1,display_mask),
        minx.XData('CARD32',1,attribute) )

class NVCtrlQueryStringAttributeReply:
    '''the reply to NVCtrlQueryStringAttribute request. returns
    the string and the flags, which describe whether attribute
    is read-only, like int version. the attribute string len
    is also returned by this variation in 'n'. n is NOT the
    length>>2, it is the true number of bytes in string. the
    'length' field is equiv to X 'size' field, 'n' is equiv
    to X 'string length' field'''

    def __init__(self,encoding):
        xreply, ad = minx.decode( encoding,
        minx.XData('BYTE',1,'type'),
        minx.XData('BYTE',1,'pad0'),
        minx.XData('CARD16',1,'sequence_number'),
        minx.XData('CARD32',1,'length'),
        minx.XData('CARD32',1,'flags'),
        minx.XData('CARD32',1,'n'),
        minx.XData('CARD32',1,'pad4'),
        minx.XData('CARD32',1,'pad5'),
        minx.XData('CARD32',1,'pad6'),
        minx.XData('CARD32',1,'pad7') )

        for n, v in xreply.iteritems():
            setattr( self, n, v )

        rs, ad = minx.decode( ad,
        minx.XData('STRING8',self.n,'string') )
        self.string = str(rs['string'])


###############################################################################
# NV-CONTROL Set String Attribute
#
class NVCtrlSetStringAttributeRequest:
    def __init__(self,nvmajor,screen,display_mask,attribute,data):
        dlen = len(data)+1 #include terminating 0
        self.encoding = minx.encode( minx.XData('CARD8',1,nvmajor),
        minx.XData('CARD8',1,X_nvCtrlSetStringAttribute),
        minx.XData('CARD16',1,5 + (((dlen+3)&~3) >> 2) ),
        minx.XData('CARD32',1,screen),
        minx.XData('CARD32',1,display_mask),
        minx.XData('CARD32',1,attribute),
        minx.XData('CARD32',1,dlen),
        minx.XData('STRING8',dlen,data+'\0'))


class NVCtrlSetStringAttributeReply:
    def __init__(self,encoding):
        xreply, ad = minx.decode( encoding,
        minx.XData('BYTE',1,'type'),
        minx.XData('BYTE',1,'pad0'),
        minx.XData('CARD16',1,'sequence_number'),
        minx.XData('CARD32',1,'length'),
        minx.XData('CARD32',1,'flags'),
        minx.XData('CARD32',1,'pad3'),
        minx.XData('CARD32',1,'pad4'),
        minx.XData('CARD32',1,'pad5'),
        minx.XData('CARD32',1,'pad6'),
        minx.XData('CARD32',1,'pad7') )

        for n, v in xreply.iteritems():
            setattr( self, n, v )


###############################################################################
# NV-CONTROL Query Valid Attribute Values
#
class NVCtrlQueryValidAttributeValuesRequest:
    '''this class handles the Query Valid Attribute Values request,
    which tells us whether or not the attribute is present, and if so,
    what the valid values for it are'''

    def __init__(self,nvmajor,target_id,target_type,display_mask,attribute):
        self.encoding = minx.encode( minx.XData('CARD8',1,nvmajor),
        minx.XData('CARD8',1,X_nvCtrlQueryValidAttributeValues),
        minx.XData('CARD16',1,4),
        minx.XData('CARD16',1,target_id),
        minx.XData('CARD16',1,target_type),
        minx.XData('CARD32',1,display_mask),
        minx.XData('CARD32',1,attribute) )


class NVCtrlQueryValidAttributeValuesReply:
    '''the reply to NVCtrlQueryValidAttributeValues request. returns
    the value and the flags, which describe whether attribute
    is read-only, etc. see NVCtrlLib.h'''

    def __init__(self,encoding):
        xreply, ad = minx.decode( encoding,
        minx.XData('BYTE',1,'type'),
        minx.XData('BYTE',1,'pad0'),
        minx.XData('CARD16',1,'sequence_number'),
        minx.XData('CARD32',1,'length'),
        minx.XData('CARD32',1,'flags'),
        minx.XData('INT32',1,'attr_type'),
        minx.XData('INT32',1,'min'),
        minx.XData('INT32',1,'max'),
        minx.XData('CARD32',1,'bits'),
        minx.XData('CARD32',1,'perms') )

        for n, v in xreply.iteritems():
            setattr( self, n, v )


###############################################################################
# NV-CONTROL String Operation
#
class NVCtrlStringOperationRequest:
    def __init__(self,nvmajor,target_id,target_type,display_mask,attribute,data):
        dlen = 0
        if data and len(data) > 0:
            dlen = len(data)+1 #include terminating 0
        else:
            data = ''
        self.encoding = minx.encode( minx.XData('CARD8',1,nvmajor),
        minx.XData('CARD8',1,X_nvCtrlSetStringAttribute),
        minx.XData('CARD16',1,5 + (((dlen+3)&~3) >> 2) ),
        minx.XData('CARD16',1,target_id),
        minx.XData('CARD16',1,target_type),
        minx.XData('CARD32',1,display_mask),
        minx.XData('CARD32',1,attribute),
        minx.XData('CARD32',1,dlen),
        minx.XData('STRING8',dlen,data+'\0'))


class NVCtrlStringOperationReply:
    def __init__(self,encoding):
        xreply, ad = minx.decode( encoding,
        minx.XData('BYTE',1,'type'),
        minx.XData('BYTE',1,'padb1'),
        minx.XData('CARD16',1,'sequence_number'),
        minx.XData('CARD32',1,'length'),
        minx.XData('CARD32',1,'flags'),
        minx.XData('CARD32',1,'n'),
        minx.XData('CARD32',1,'padl4'),
        minx.XData('CARD32',1,'padl5'),
        minx.XData('CARD32',1,'padl6'),
        minx.XData('CARD32',1,'padl7') )

        for n, v in xreply.iteritems():
            setattr( self, n, v )

        rs, ad = minx.decode( ad,
        minx.XData('STRING8',self.n,'string') )
        self.string = str(rs['string'])




def get_NV_CONTROL_version( xsock, nvmajor ):
    ''' this function uses NVCtrlQueryExtension to get
    the major and minor versions of the NV-CONTROL extension
    in use. returned as a tuple (major,minor)'''

    rq = NVCtrlQueryExtensionRequest( nvmajor )
    binrp = minx.Xchange( xsock, rq )

    if binrp[0] == 0:
        raise minx.XServerError( binrp )
    else:
        nvc = NVCtrlQueryExtensionReply( binrp )
        return (nvc.major,nvc.minor)


def query_int_attribute( xsock, nvmajor, target_id, target_type,
    display_mask, attribute):

    rq = NVCtrlQueryAttributeRequest( nvmajor, target_id,
    target_type, display_mask, attribute )
    binrp = minx.Xchange( xsock, rq )

    if binrp[0] == 0:
        raise minx.XServerError( binrp )
    else:
        return NVCtrlQueryAttributeReply( binrp )


def set_int_attribute( xsock, nvmajor, screen, display_mask,
    attribute, value ):

    rq = NVCtrlSetAttributeAndGetStatusRequest( nvmajor, screen,
    display_mask, attribute, value )
    binrp = minx.Xchange( xsock, rq )

    if binrp[0] == 0:
        raise minx.XServerError( binrp )
    else:
        return NVCtrlSetAttributeAndGetStatusReply( binrp )


def query_string_attribute( xsock, nvmajor, target_id, target_type,
    display_mask, attribute):

    rq = NVCtrlQueryStringAttributeRequest( nvmajor, target_id,
    target_type, display_mask, attribute )
    binrp = minx.Xchange( xsock, rq )

    if binrp[0] == 0:
        raise minx.XServerError( binrp )
    else:
        return NVCtrlQueryStringAttributeReply( binrp )


def set_string_attribute( xsock, nvmajor, screen, display_mask,
    attribute, data):

    rq = NVCtrlSetStringAttributeRequest( nvmajor, screen,
    display_mask, attribute, data)
    binrp = minx.Xchange( xsock, rq )

    if binrp[0] == 0:
        raise minx.XServerError( binrp )
    else:
        return NVCtrlSetStringAttributeReply( binrp )


def query_target_count( xsock, nvmajor, target ):

    rq = NVCtrlQueryTargetCountRequest( nvmajor, target )
    binrp = minx.Xchange( xsock, rq )

    if binrp[0] == 0:
        raise minx.XServerError( binrp )
    else:
        return NVCtrlQueryTargetCountReply( binrp )


def query_binary_data( xsock, nvmajor, target_id, target_type,
    display_mask, attribute):

    rq = NVCtrlQueryBinaryDataRequest( nvmajor, target_id,
    target_type, display_mask, attribute )
    binrp = minx.Xchange( xsock, rq )

    if binrp[0] == 0:
        raise minx.XServerError( binrp )
    else:
        return NVCtrlQueryBinaryDataReply( binrp )


def query_valid_attribute_values( xsock, nvmajor, target_id, target_type,
    display_mask, attribute):

    rq = NVCtrlQueryValidAttributeValuesRequest( nvmajor, target_id,
    target_type, display_mask, attribute )
    binrp = minx.Xchange( xsock, rq )

    if binrp[0] == 0:
        raise minx.XServerError( binrp )
    else:
        return NVCtrlQueryValidAttributeValuesReply( binrp )


def get_valid_attribute_values( xsock, nvmajor, ngpu, attr ):
    vv = query_valid_attribute_values( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, attr )

    return vv


def string_operation( xsock, nvmajor, target_id, target_type,
    display_mask, attribute, data):

    rq = NVCtrlStringOperationRequest( nvmajor, target_id,
    target_type, display_mask, attribute, data )
    binrp = minx.Xchange( xsock, rq )

    if binrp[0] == 0:
        raise minx.XServerError( binrp )
    else:
        return NVCtrlStringOperationReply( binrp )


def get_GPU_count( xsock, nvmajor ):
    gpc = query_target_count( xsock, nvmajor, NV_CTRL_TARGET_TYPE_GPU )
    return gpc.count


def get_GPU_bus_type( xsock, nvmajor, ngpu ):
    br = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_BUS_TYPE )

    return __BUS_TYPES[br.value]


def get_GPU_vram( xsock, nvmajor, ngpu ):
    vr = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_VIDEO_RAM )

    return vr.value / 1024


def get_GPU_IRQ( xsock, nvmajor, ngpu ):
    irq = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_IRQ )

    return irq.value


def get_GPU_connected_display_mask( xsock, nvmajor, ngpu ):
    cd = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_CONNECTED_DISPLAYS )

    return cd.value


def get_GPU_enabled_display_mask( xsock, nvmajor, ngpu ):
    ed = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_ENABLED_DISPLAYS )

    return ed.value


def GPU_supports_framelock( xsock, nvmajor, ngpu ):
    fl = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_FRAMELOCK )

    if fl.value == 1:
        return True
    else:
        return False


def get_GPU_name( xsock, nvmajor, ngpu ):
    ns = query_string_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_STRING_PRODUCT_NAME )

    return ns.string


def get_current_modeline( xsock, nvmajor, ngpu ):
    dm = query_string_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_STRING_CURRENT_MODELINE )

    return dm.string


def get_OS_type( xsock, nvmajor ):
    ot = query_int_attribute( xsock, nvmajor, 0,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_OPERATING_SYSTEM )

    return __OS_TYPES[ot.value]


def get_host_architecture( xsock, nvmajor ):
    ha = query_int_attribute( xsock, nvmajor, 0,
    NV_CTRL_TARGET_TYPE_X_SCREEN, 0, NV_CTRL_ARCHITECTURE )

    return __ARCH_TYPES[ha.value]


def GVO_supported( xsock, nvmajor ):
    gv = query_int_attribute( xsock, nvmajor, 0,
    NV_CTRL_TARGET_TYPE_X_SCREEN, 0, NV_CTRL_GVO_SUPPORTED )

    if gv.value == 1:
        return True
    else:
        return False


def get_GPU_core_temp( xsock, nvmajor, ngpu ):
    ct = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_GPU_CORE_TEMPERATURE )

    return ct.value


def get_GPU_core_threshold( xsock, nvmajor, ngpu ):
    th = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_GPU_CORE_THRESHOLD )

    return th.value


def get_GPU_default_core_threshold( xsock, nvmajor, ngpu ):
    dt = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_GPU_DEFAULT_CORE_THRESHOLD )

    return dt.value


def get_GPU_max_core_threshold( xsock, nvmajor, ngpu ):
    mt = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_GPU_MAX_CORE_THRESHOLD )

    return mt.value


def get_GPU_ambient_temp( xsock, nvmajor, ngpu ):
    at = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_AMBIENT_TEMPERATURE )

    return at.value

def get_GPU_2D_clocks( xsock, nvmajor, ngpu ):
    cl = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_GPU_2D_CLOCK_FREQS )

    return (cl.value >> 16, cl.value & 0xFFFF)


def get_GPU_3D_clocks( xsock, nvmajor, ngpu ):
    cl = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_GPU_3D_CLOCK_FREQS )

    return (cl.value >> 16, cl.value & 0xFFFF)


def get_GPU_default_2D_clocks( xsock, nvmajor, ngpu ):
    dc = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_GPU_DEFAULT_2D_CLOCK_FREQS )

    return (dc.value >> 16, dc.value & 0xFFFF)


def get_GPU_default_3D_clocks( xsock, nvmajor, ngpu ):
    dc = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_GPU_DEFAULT_3D_CLOCK_FREQS )

    return (dc.value >> 16, dc.value & 0xFFFF)


def get_GPU_current_clocks( xsock, nvmajor, ngpu ):
    cf = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_GPU_CURRENT_CLOCK_FREQS )

    return (cf.value >> 16, cf.value & 0xFFFF)


def GPU_Xinerama_enabled( xsock, nvmajor, ngpu ):
    xn = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_XINERAMA )

    if xn.value == 1:
        return True
    else:
        return False


def get_GPU_refresh_rate( xsock, nvmajor, ngpu ):
    rr = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 1, NV_CTRL_REFRESH_RATE )

    return rr.value / 1000


def get_GPU_displays( xsock, nvmajor, ngpu ):
    md = query_int_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 0, NV_CTRL_PROBE_DISPLAYS)

    displays = []
    for idisp in range(0,24):
        disp = 1 << idisp
        if md.value & disp:
            displays.append(idisp)

    return displays


def get_GPU_display_name( xsock, nvmajor, ngpu, ndisp ):
    ns = query_string_attribute( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 1<<ndisp, NV_CTRL_STRING_DISPLAY_DEVICE_NAME )

    return ns.string


def get_GPU_display_modelines( xsock, nvmajor, ngpu, ndisp ):
    mls = query_binary_data( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 1<<ndisp, NV_CTRL_BINARY_DATA_MODELINES )

    return filter(lambda x: x, mls.data.split('\0'))


def get_screen_metamodes( xsock, nvmajor, nscreen ):
    mms = query_binary_data( xsock, nvmajor, nscreen,
    NV_CTRL_TARGET_TYPE_X_SCREEN, 0, NV_CTRL_BINARY_DATA_METAMODES)

    return filter(lambda x: x, mms.data.split('\0'))


def add_screen_metamode( xsock, nvmajor, nscreen, mm ):
    res = set_string_attribute( xsock, nvmajor, nscreen,
    0, NV_CTRL_STRING_ADD_METAMODE, mm )

    return res.flags


def delete_screen_metamode( xsock, nvmajor, nscreen, mm ):
    res = set_string_attribute( xsock, nvmajor, nscreen,
    0, NV_CTRL_STRING_DELETE_METAMODE, mm )

    return res.flags


def build_GPU_modepool( xsock, nvmajor, ngpu, ndisp ):
    res = string_operation( xsock, nvmajor, ngpu,
    NV_CTRL_TARGET_TYPE_GPU, 1<<ndisp, NV_CTRL_STRING_OPERATION_BUILD_MODEPOOL, None )

    return res.string


def set_screen_associated_displays( xsock, nvmajor, nscreen, disp ):
    disp = _get_dispmask(disp)
    res = set_int_attribute( xsock, nvmajor, nscreen,
         disp, NV_CTRL_ASSOCIATED_DISPLAY_DEVICES, disp )

    return res.flags


def set_screen_scaling( xsock, nvmajor, nscreen, disp, target, method):
    disp = _get_dispmask(disp)
    res = set_int_attribute( xsock, nvmajor, nscreen,
        disp, NV_CTRL_GPU_SCALING, (target<<16) + method )

    return res.flags



def _get_dispmask( disp ):
    '''return display mask from either an integer or an array of display numbers'''
    if type(disp) != list:
        return disp
    dispmask = 0
    for ndisp in disp: dispmask += 1 << ndisp
    return dispmask

