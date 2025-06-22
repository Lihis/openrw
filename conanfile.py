from conan import ConanFile
from conan.tools.cmake import CMake


class OpenrwConan(ConanFile):
    name = 'openrw'
    version = 'main'
    license = 'GPL3'
    url = 'https://github.com/rwengine/openrw'
    description = "OpenRW 'Open ReWrite' is an un-official open source recreation of the classic Grand Theft Auto III game executable"
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {
        'viewer': [True, False],
        'tools': [True, False],
        'profiling': [True, False],
    }

    default_options = {
        'viewer': True,
        'tools': True,
        'profiling': True,
        'bullet3/*:shared': False,
    }

    generators = 'CMakeDeps', 'CMakeToolchain'
    exports_sources = 'CMakeLists.txt', 'cmake_configure.cmake', 'cmake_options.cmake', 'CMakeCPack.cmake', 'COPYING', \
                      'cmake/modules/*', 'benchmarks', 'rwcore/*', 'rwengine/*', 'rwgame/*', 'rwviewer/*', \
                      'rwtools/*', 'tests/*', 'external/*'

    _rw_dependencies = {
        'game': (
            'openal/1.22.2',
            'bullet3/3.25',
            'glm/1.0.1',
            'ffmpeg/7.1.1',
            'sdl/3.2.14',
            'boost/1.88.0',
            'bzip2/1.0.8',
        ),
        'viewer': (
            'qt/5.15.16',
        ),
        'tools': (
            'freetype/2.13.2',
        ),
    }

    def configure(self):
        if self.options.viewer:
            self.options['qt'].opengl = 'dynamic'

    def requirements(self):
        for dep in self._rw_dependencies['game']:
            self.requires(dep)
        if self.options.viewer:
            for dep in self._rw_dependencies['viewer']:
                self.requires(dep)
        if self.options.tools:
            for dep in self._rw_dependencies['tools']:
                self.requires(dep)

    def _configure_cmake(self):
        cmake = CMake(self)
        defs = {
            'BUILD_SHARED_LIBS': False,
            'CMAKE_BUILD_TYPE': self.settings.build_type,
            'BUILD_TESTS': True,
            'BUILD_VIEWER': self.options.viewer,
            'BUILD_TOOLS': self.options.tools,
            'ENABLE_PROFILING': self.options.profiling,
            'USE_CONAN': True,
            'BOOST_STATIC': not self.options['boost'].shared,
        }

        cmake.configure(defs=defs)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        if self.options.viewer:
            # FIXME: https://github.com/osechet/conan-qt/issues/6 and https://github.com/conan-io/conan/issues/2619
            self.copy('qt.conf', dst='bin', src='rwviewer')
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['rwengine', 'rwlib']
        self.cpp_info.stdcpp = 17
