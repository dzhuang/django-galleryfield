from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

def read(fname):
    # file read function copied from sorl.django-documents project
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_requires = [
    'sorl-thumbnail',
    'pillow'
]

setup(
    name='django-gallery-widget',
    version=version,
    description="Django AJAX upload widget and model field for multiple images, featuring drag & drop uploading, upload progress bar, sortable and croppable image gallery",
    long_description=read('README.md'),
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django ajax html5 upload widget images gallery sorting crop progress'
             'thumbnails multiple galleryfield admin forms field',
    author='Dong Zhuang',
    author_email='dzhuang.scut@gmail.com',
    url='https://github.com/dzhuang/django-gallery-widget',
    license='MIT',
    packages=find_packages(exclude=['tests', 'demo']),
    include_package_data=True,
    zip_safe=True,
    install_requires=install_requires,
    entry_points="""
        # -*- Entry points: -*-
    """,
)
