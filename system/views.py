# from django.views.generic import DetailView, UpdateView, CreateView
# from django.db import transaction
# from django.urls import reverse_lazy
# from django.contrib.messages.views import SuccessMessageMixin
# from django.contrib.auth.views import LoginView, LogoutView
# from .forms import UserPasswordChangeForm
# from django.contrib.auth.views import PasswordChangeView
# from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
#
# from .models import Profile
# from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, UserLoginForm
# from .forms import UserForgotPasswordForm, UserSetNewPasswordForm
#
#
# class ProfileDetailView(DetailView):
#     """
#     Представление для просмотра профиля
#     """
#     model = Profile
#     context_object_name = 'profile'
#     template_name = 'profile_detail.html'
#     queryset = model.objects.all().select_related('user')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = f'Страница пользователя: {self.object.user.username}'
#         return context
#
#
# class ProfileUpdateView(UpdateView):
#     """
#     Представление для редактирования профиля
#     """
#     model = Profile
#     form_class = ProfileUpdateForm
#     template_name = 'profile_edit.html'
#
#     def get_object(self, queryset=None):
#         return self.request.user.profile
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'
#         if self.request.POST:
#             context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
#         else:
#             context['user_form'] = UserUpdateForm(instance=self.request.user)
#         return context
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         user_form = context['user_form']
#         with transaction.atomic():
#             if all([form.is_valid(), user_form.is_valid()]):
#                 user_form.save()
#                 form.save()
#             else:
#                 context.update({'user_form': user_form})
#                 return self.render_to_response(context)
#         return super(ProfileUpdateView, self).form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('profile_detail', kwargs={'slug': self.object.slug})
#
#
# class UserRegisterView(SuccessMessageMixin, CreateView):
#     """
#     Представление регистрации на сайте с формой регистрации
#     """
#     form_class = UserRegisterForm
#     success_url = reverse_lazy('search_cafes')
#     template_name = 'user_register.html'
#     success_message = 'Вы успешно зарегистрировались. Можете войти на сайт!'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Регистрация на сайте'
#         return context
#
#
# class UserLoginView(SuccessMessageMixin, LoginView):
#     """
#     Авторизация на сайте
#     """
#     form_class = UserLoginForm
#     template_name = 'user_login.html'
#     next_page = 'search_cafes'
#     success_message = 'Добро пожаловать на сайт!'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Авторизация на сайте'
#         return context
#
#
# class UserLogoutView(LogoutView):
#     """
#     Выход с сайта
#     """
#     next_page = 'search_cafes'
#
#
# class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
#     """
#     Изменение пароля пользователя
#     """
#     form_class = UserPasswordChangeForm
#     template_name = 'password-change.html'
#     success_message = 'Ваш пароль был успешно изменён!'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Изменение пароля на сайте'
#         return context
#
#     def get_success_url(self):
#         return reverse_lazy('profile_detail', kwargs={'slug': self.request.user.profile.slug})
#
#
# class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
#     """
#     Представление по сбросу пароля по почте
#     """
#     form_class = UserForgotPasswordForm
#     template_name = 'password-reset.html'
#     success_url = reverse_lazy('search_cafes')
#     success_message = 'Письмо с инструкцией по восстановлению пароля отправлена на ваш email'
#     subject_template_name = 'email/password-subject-reset-mail.html'
#     email_template_name = 'email/password-reset-mail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Запрос на восстановление пароля'
#         return context
#
#
# class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
#     """
#     Представление установки нового пароля
#     """
#     form_class = UserSetNewPasswordForm
#     template_name = 'password-set-new.html'
#     success_url = reverse_lazy('search_cafes')
#     success_message = 'Пароль успешно изменен. Можете авторизоваться на сайте.'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Установить новый пароль'
#         return context


from django.views.generic import DetailView, UpdateView, CreateView, View, TemplateView
from django.db import transaction
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView, LogoutView
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib.auth import login

from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, UserLoginForm, UserPasswordChangeForm, \
    UserForgotPasswordForm, UserSetNewPasswordForm
from system.services.mixins import UserIsNotAuthenticated

User = get_user_model()


class ProfileDetailView(DetailView):
    """
    Представление для просмотра профиля
    """
    model = Profile
    context_object_name = 'profile'
    template_name = 'profile_detail.html'
    queryset = model.objects.all().select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Страница пользователя: {self.object.user.username}'
        return context


class ProfileUpdateView(UpdateView):
    """
    Представление для редактирования профиля
    """
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'
        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()
            else:
                context.update({'user_form': user_form})
                return self.render_to_response(context)
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'slug': self.object.slug})


class UserLoginView(SuccessMessageMixin, LoginView):
    """
    Авторизация на сайте
    """
    form_class = UserLoginForm
    template_name = 'user_login.html'
    next_page = 'home'
    success_message = 'Добро пожаловать на сайт!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация на сайте'
        return context


class UserLogoutView(LogoutView):
    """
    Выход с сайта
    """
    next_page = 'home'



class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """
    Изменение пароля пользователя
    """
    form_class = UserPasswordChangeForm
    template_name = 'user_password_change.html'
    success_message = 'Ваш пароль был успешно изменён!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменение пароля на сайте'
        return context

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'slug': self.request.user.profile.slug})


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """
    Представление по сбросу пароля по почте
    """
    form_class = UserForgotPasswordForm
    template_name = 'user_password_reset.html'
    success_url = reverse_lazy('home')
    success_message = 'Письмо с инструкцией по восстановлению пароля отправлена на ваш email'
    subject_template_name = 'system/email/password_subject_reset_mail.txt'
    email_template_name = 'system/email/password_reset_mail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Запрос на восстановление пароля'
        return context


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Представление установки нового пароля
    """
    form_class = UserSetNewPasswordForm
    template_name = 'user_password_set_new.html'
    success_url = reverse_lazy('home')
    success_message = 'Пароль успешно изменен. Можете авторизоваться на сайте.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Установить новый пароль'
        return context


class UserRegisterView(UserIsNotAuthenticated, CreateView):
    """
    Представление регистрации на сайте с формой регистрации
    """
    form_class = UserRegisterForm
    success_url = reverse_lazy('home')
    template_name = 'user_register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация на сайте'
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        # Функционал для отправки письма и генерации токена
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = reverse_lazy('confirm_email', kwargs={'uidb64': uid, 'token': token})
        current_site = Site.objects.get_current().domain
        send_mail(
            'Подтвердите свой электронный адрес',
            f'Пожалуйста, перейдите по следующей ссылке, чтобы подтвердить свой адрес электронной почты: http://{current_site}{activation_url}',
            'amikphoto@yandex.ru',
            [user.email],
            fail_silently=False,
        )
        return redirect('email_confirmation_sent')


class UserConfirmEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('email_confirmed')
        else:
            return redirect('email_confirmation_failed')


class EmailConfirmationSentView(TemplateView):
    template_name = 'system/registration/email_confirmation_sent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Письмо активации отправлено'
        return context


class EmailConfirmedView(TemplateView):
    template_name = 'system/registration/email_confirmed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес активирован'
        return context


class EmailConfirmationFailedView(TemplateView):
    template_name = 'system/registration/email_confirmation_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес не активирован'
        return context