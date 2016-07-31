from django.shortcuts import render_to_response
from testpooldb import models

class ProfileView(object):
    def __init__(self, profile):
        """Contruct a product view. """
        self.name = profile.name
        self.vm_max = profile.vm_max
        self.vm_free = 0
        self.vm_reserved = 0
        self.vm_released = 0

        for item in models.VM.objects.filter(profile=profile):
            if item.status == VM.RESERVED:
                self.vm_reserved += 1
            elif item.status == VM.RELEASED:
                self.vm_released += 1
            elif status == VM.FREE:
                self.vm_released += 1

def index(_):
    """ Summarize product information. """

    profiles = models.Profile.objects.all()
    profiles = [ProfileView(item) for item in profiles]

    html_data = {"profiles": profiles}
    return render_to_response("profile/index.html", html_data)
