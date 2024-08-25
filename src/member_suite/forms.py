from django import forms

class BookKilnForm(forms.Form):
    """
    Description:
        Form to collect information required for booking a timeslot

    Related Model:
        BookingManagement

    Security:
        TODO
        Gaurentee day format is correct upon submission
        Gaurentee the timeslot ID is from a studio they own or have a member relationship to.
    """

    book_timeslot = forms.IntegerField(widget=forms.HiddenInput(attrs={'readonly': 'readonly'}))
    day = forms.CharField(widget=forms.HiddenInput(attrs={'readonly': 'readonly'})) #("%Y-%m-%d")

class UnbookKilnForm(forms.Form):
    """
    Description:
        Form required for automatic filling out of hidden fields

    Related Model:
        BookingManagement

    Security:
        TODO
        Encrypt values that are entered into the form and decrypt them upon submission.
        Make sure the timeslot is one they have booked and they're not somehow unbooking someone elses timeslot.
    """

    unbook_timeslot = forms.IntegerField(widget=forms.HiddenInput(attrs={'readonly': 'readonly'}))
    unbook_date = forms.CharField(widget=forms.HiddenInput(attrs={'readonly': 'readonly'})) #("%Y-%m-%d")
