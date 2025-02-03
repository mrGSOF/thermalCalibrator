from . import ITS27, IPTS68

class ITS68(ITS27.ITS27):
    """
    Calculate the ITS68 correction.
    This correction should be calculated for a temperature value that was derived
    from Van-Dusen calaculation.
    """

    def T(self, R):
        """
        Return the corrected temperature in [C] after applying the ITS68 correction.
        The input should be the resistance of the sensor in [Ohm]
        """
        T = ITS27.ITS27.T(self, R)
        corr = IPTS68.ipts68(T)
        return T + corr
