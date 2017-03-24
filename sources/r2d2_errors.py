class R2D2_Error(Exception):
    """Base class for exceptions."""
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)


class R2D2_RedditError(R2D2_Error):
    def __init__(self,*args,**kwargs):
        R2D2_Error.__init__(self,*args,**kwargs)


class R2D2_ConfigurationError(R2D2_Error):
    def __init__(self,*args,**kwargs):
        R2D2_Error.__init__(self,*args,**kwargs)


class R2D2_DatabaseError(R2D2_Error):
    def __init__(self,*args,**kwargs):
        R2D2_Error.__init__(self,*args,**kwargs)
