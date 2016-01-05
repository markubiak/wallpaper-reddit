from setuptools import setup

setup(
        name='Wallpaper Reddit',
        version='2.0',
        packages=['wpreddit'],
        url='https://www.github.com/markubiak/wallpaper-reddit',
        author='Mark Kubiak',
        author_email='mkubiak.dev@gmail.com',
        description='A utility that downloads wallpapers from reddit',
        install_requires=['Pillow>=3.0'],
        entry_points={
            'console_scripts': [
                'wallpaper-reddit = wpreddit.main:run'
                ]
            }
)
