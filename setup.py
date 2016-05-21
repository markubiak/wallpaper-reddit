from setuptools import setup, find_packages

setup(
        name='wallpaper-reddit',
        version='3.0.0',
        packages=find_packages(),
        url='https://www.github.com/markubiak/wallpaper-reddit',
        author='Mark Kubiak',
        author_email='mkubiak.dev@gmail.com',
        description='A utility that downloads wallpapers from reddit',
        install_requires=['Pillow>=3.0'],
        package_data={
            'wpreddit': ['fonts/*.otf', 'conf_files/*.conf']
        },
        entry_points={
            'console_scripts': [
                'wallpaper-reddit = wpreddit.main:run'
            ]
        }
)
