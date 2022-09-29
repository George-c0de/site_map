from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import gettext_lazy as _


class Coords(models.Model):
    name = models.CharField('Адрес', max_length=150, default='')
    coords_x = models.DecimalField('X', max_digits=17, decimal_places=15)
    coords_y = models.DecimalField('Y', max_digits=17, decimal_places=15)

    class Meta:
        verbose_name_plural = _("Координаты пользователей")


# class UserManager(BaseUserManager):
#     use_in_migrations = True
#
#     def _create_user(self, email, password, **extra_fields):
#         """
#         Create and save a user with the given username, email, and password.
#         """
#         if not email:
#             raise ValueError("The given username must be set")
#         email = self.normalize_email(email)
#         # Lookup the real model class from the global app registry so this
#         # manager method can be used in migrations. This is fine because
#         # managers are by definition working on the real model.
#         user = self.model(email=email, **extra_fields)
#         user.password = make_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_user(self, email, password=None, **extra_fields):
#         return self._create_user(email, password, **extra_fields)
#
#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault("is_superuser", True)
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser=True.")
#
#         return self._create_user(email, password, **extra_fields)
#
#     def with_perm(
#             self, perm, is_active=True, include_superusers=True, backend=None, obj=None
#     ):
#         if backend is None:
#             backends = auth._get_backends(return_tuples=True)
#             if len(backends) == 1:
#                 backend, _ = backends[0]
#             else:
#                 raise ValueError(
#                     "You have multiple authentication backends configured and "
#                     "therefore must provide the `backend` argument."
#                 )
#         elif not isinstance(backend, str):
#             raise TypeError(
#                 "backend must be a dotted import path string (got %r)." % backend
#             )
#         else:
#             backend = auth.load_backend(backend)
#         if hasattr(backend, "with_perm"):
#             return backend.with_perm(
#                 perm,
#                 is_active=is_active,
#                 include_superusers=include_superusers,
#                 obj=obj,
#             )
#         return self.none()
#
#
# class User(AbstractBaseUser, PermissionsMixin):
#     patronymic = models.CharField(_("Отчество"), max_length=150, blank=True)
#     first_name = models.CharField(_("Имя"), max_length=150, blank=True)
#     last_name = models.CharField(_("Фамилия"), max_length=150, blank=True)
#     email = models.EmailField(_("email address"), unique=True)
#
#     objects = UserManager()
#
#     EMAIL_FIELD = "email"
#     USERNAME_FIELD = "email"
#
#     # REQUIRED_FIELDS = ["email"]
#
#     class Meta:
#         verbose_name = _("Пользователь")
#         verbose_name_plural = _("Пользователи")
#
#     def clean(self):
#         super().clean()
#         self.email = self.__class__.objects.normalize_email(self.email)
#
#     def get_full_name(self):
#         """
#         Return the first_name plus the last_name, with a space in between.
#         """
#         full_name = "%s %s" % (self.first_name, self.last_name)
#         return full_name.strip()
#
#     def get_short_name(self):
#         """Return the short name for the user."""
#         return self.first_name
#
#     def email_user(self, subject, message, from_email=None, **kwargs):
#         """Send an email to this user."""
#         send_mail(subject, message, from_email, [self.email], **kwargs)
#

class Image(models.Model):
    image = models.ImageField('/', blank=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card = models.OneToOneField(Coords, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.OneToOneField(Image, on_delete=models.CASCADE, null=True, blank=True)
    patronymic = models.CharField('Отчество', max_length=150, null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Пользователь")
