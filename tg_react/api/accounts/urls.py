from django.conf.urls import url

from .views import UserDetails, AuthenticationView, LogoutView, SignUpView
from .views import ForgotPassword
from .views import RestorePassword


urlpatterns = [
    url(r'^me$', UserDetails.as_view(), name='api-user-details'),
    url(r'^login$', AuthenticationView.as_view(), name='api-user-login'),
    url(r'^logout$', LogoutView.as_view(), name='api-user-logout'),
    # signup
    url(r'^signup$', SignUpView.as_view(), name='api-signup'),
    # password recovery
    url(r'^forgot_password$', ForgotPassword.as_view(), name='api-forgot-password'),
    url(r'^forgot_password/token$', RestorePassword.as_view(), name='api-forgot-password-token'),
]