#coding=utf-8
from django.db import models
from django.db.models import signals
from django.dispatch import dispatcher

# Create your models here.
#This model is used to save the parser type, and modelname is
#used to save the source code name
class Tag(models.Model):
    name = models.CharField(maxlength=20)
    
    def __unicode__(self):
        return self.name
    
    class Admin:
        pass
    
C_STATUS = [(0, 'waiting'), (1, 'processing'), (2, 'done')]
class Book(models.Model):
    name = models.CharField(maxlength=100, db_index=True)
    status = models.IntegerField(choices=C_STATUS, default=0)
    url = models.URLField()
    date = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag)
    count = models.IntegerField(default=0)
    finished = models.IntegerField(default=0)
    message = models.CharField(maxlength=100, default='')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['-name']
    
    class Admin:
        pass
    
class Chapter(models.Model):
    order = models.IntegerField()
    name = models.CharField(maxlength=200, db_index=True)
    url = models.URLField()
    content = models.TextField(default='')
    book = models.ForeignKey(Book)
    size = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __unicode__(self):
        return self.name
    
    class Admin:
        pass
    
def post_save_chapter(sender, instance, signal, *args, **kwargs):
    try:
        book = Book.objects.get(id=instance.book.id)
    except Book.DoesNotExist:
        return
    book.finished = book.chapter_set.filter(size__gt=0).count()
    book.save()
dispatcher.connect(post_save_chapter , signal=signals.post_save, sender=Chapter)
