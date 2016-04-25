from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True, default=None)
    color = models.ForeignKey('Colors', default=None, blank=True, null=True,
                              related_name='colors', on_delete=models.SET_NULL)
    category = models.ManyToManyField('Categories', default=None, blank=True,
                                      related_name='categories')
    owner = models.ForeignKey(User)
    delegated = models.ManyToManyField(User, blank=True,
                                       related_name='users_allow')
    label = models.ManyToManyField('Labels', blank=True,
                                   related_name='labels')
    date_create = models.DateTimeField(auto_now_add=True)
    date_editing = models.DateTimeField(auto_now=True)
    content = models.TextField()
    file = models.ManyToManyField('Attachments', blank=True,
                                  related_name='attach')

    def __str__(self):
        if not self.title:
            return 'Untitled'
        return self.title

    class Meta:
        db_table = 'notes'
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'


class Colors(models.Model):
    # only color HEX
    color = models.CharField(max_length=7)

    def __str__(self):
        return self.color

    class Meta:
        db_table = 'colors'
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'


class Categories(models.Model):
    title = models.CharField(max_length=200)
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='sub_category', on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Labels(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'labels'
        verbose_name = 'Label'
        verbose_name_plural = 'Labels'


def content_file_name(instance, filename):
    return '/'.join(['attachments', instance.owner.username, filename])


def preview_file_name(instance, filename):
    return '/'.join(['attachments', instance.owner.username, 'preview', filename])


class Attachments(models.Model):
    title = models.CharField(max_length=200, default='No name')
    file = models.FileField(upload_to=content_file_name)
    preview = models.ImageField(upload_to=preview_file_name, blank=True, null=True)
    owner = models.ForeignKey(User)

    def delete_images(self):
        """
        Delete files from file system when it delete from db.
        """
        import os
        links = []
        if self.file:
            links.append(self.file.path)
        if self.preview:
            links.append(self.preview.path)
        for i in links:
            try:
                os.remove(i)
            except FileNotFoundError:
                pass

    def delete(self, *args, **kwargs):
        """
        We must delete all old images from server.
        :param args:
        :param kwargs:
        :return:
        """
        self.delete_images()
        super(Attachments, self).delete(*args, **kwargs)

    def __str__(self):
        return self.title
