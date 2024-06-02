project('dictionary',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')

python = import('python')
python_exe = python.find_installation('python3')

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)

install_data('data/dictionary.svg',
  install_dir: join_paths(get_option('datadir'), 'icons/hicolor/scalable/apps'),
  rename: 'net.aidancornelius.Dictionary.svg'
)
