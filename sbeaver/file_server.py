# -*- coding: utf-8 -*-

import sbeaver
import urllib
import html
import sys
import os
import io

types = {
    'js': 'application/javascript',
    'mjs': 'application/javascript',
    'json': 'application/json',
    'webmanifest': 'application/manifest+json',
    'doc': 'application/msword',
    'dot': 'application/msword',
    'wiz': 'application/msword',
    'bin': 'application/octet-stream',
    'a': 'application/octet-stream',
    'dll': 'application/octet-stream',
    'exe': 'application/octet-stream',
    'o': 'application/octet-stream',
    'obj': 'application/octet-stream',
    'so': 'application/octet-stream',
    'oda': 'application/oda',
    'pdf': 'application/pdf',
    'p7c': 'application/pkcs7-mime',
    'ps': 'application/postscript',
    'ai': 'application/postscript',
    'eps': 'application/postscript',
    'm3u': 'application/vnd.apple.mpegurl',
    'm3u8': 'application/vnd.apple.mpegurl',
    'xls': 'application/vnd.ms-excel',
    'xlb': 'application/vnd.ms-excel',
    'ppt': 'application/vnd.ms-powerpoint',
    'pot': 'application/vnd.ms-powerpoint',
    'ppa': 'application/vnd.ms-powerpoint',
    'pps': 'application/vnd.ms-powerpoint',
    'pwz': 'application/vnd.ms-powerpoint',
    'wasm': 'application/wasm',
    'bcpio': 'application/x-bcpio',
    'cpio': 'application/x-cpio',
    'csh': 'application/x-csh',
    'dvi': 'application/x-dvi',
    'gtar': 'application/x-gtar',
    'hdf': 'application/x-hdf',
    'h5': 'application/x-hdf5',
    'latex': 'application/x-latex',
    'mif': 'application/x-mif',
    'cdf': 'application/x-netcdf',
    'nc': 'application/x-netcdf',
    'p12': 'application/x-pkcs12',
    'pfx': 'application/x-pkcs12',
    'ram': 'application/x-pn-realaudio',
    'pyc': 'application/x-python-code',
    'pyo': 'application/x-python-code',
    'sh': 'application/x-sh',
    'shar': 'application/x-shar',
    'swf': 'application/x-shockwave-flash',
    'sv4cpio': 'application/x-sv4cpio',
    'sv4crc': 'application/x-sv4crc',
    'tar': 'application/x-tar',
    'tcl': 'application/x-tcl',
    'tex': 'application/x-tex',
    'texi': 'application/x-texinfo',
    'texinfo': 'application/x-texinfo',
    'roff': 'application/x-troff',
    't': 'application/x-troff',
    'tr': 'application/x-troff',
    'man': 'application/x-troff-man',
    'me': 'application/x-troff-me',
    'ms': 'application/x-troff-ms',
    'ustar': 'application/x-ustar',
    'src': 'application/x-wais-source',
    'xsl': 'application/xml',
    'rdf': 'application/xml',
    'wsdl': 'application/xml',
    'xpdl': 'application/xml',
    'zip': 'application/zip',
    '3gp': 'audio/3gpp',
    '3gpp': 'audio/3gpp',
    '3g2': 'audio/3gpp2',
    '3gpp2': 'audio/3gpp2',
    'aac': 'audio/aac',
    'adts': 'audio/aac',
    'loas': 'audio/aac',
    'ass': 'audio/aac',
    'au': 'audio/basic',
    'snd': 'audio/basic',
    'mp3': 'audio/mpeg',
    'mp2': 'audio/mpeg',
    'opus': 'audio/opus',
    'aif': 'audio/x-aiff',
    'aifc': 'audio/x-aiff',
    'aiff': 'audio/x-aiff',
    'ra': 'audio/x-pn-realaudio',
    'wav': 'audio/x-wav',
    'gif': 'image/gif',
    'ief': 'image/ief',
    'jpg': 'image/jpeg',
    'jpe': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'heic': 'image/heic',
    'heif': 'image/heif',
    'png': 'image/png',
    'svg': 'image/svg+xml',
    'tiff': 'image/tiff',
    'tif': 'image/tiff',
    'ico': 'image/vnd.microsoft.icon',
    'ras': 'image/x-cmu-raster',
    'bmp': 'image/x-ms-bmp',
    'pnm': 'image/x-portable-anymap',
    'pbm': 'image/x-portable-bitmap',
    'pgm': 'image/x-portable-graymap',
    'ppm': 'image/x-portable-pixmap',
    'rgb': 'image/x-rgb',
    'xbm': 'image/x-xbitmap',
    'xpm': 'image/x-xpixmap',
    'xwd': 'image/x-xwindowdump',
    'eml': 'message/rfc822',
    'mht': 'message/rfc822',
    'mhtml': 'message/rfc822',
    'nws': 'message/rfc822',
    'css': 'text/css',
    'csv': 'text/csv',
    'html': 'text/html',
    'htm': 'text/html',
    'txt': 'text/plain',
    'bat': 'text/plain',
    'c': 'text/plain',
    'h': 'text/plain',
    'ksh': 'text/plain',
    'pl': 'text/plain',
    'rtx': 'text/richtext',
    'tsv': 'text/tab-separated-values',
    'py': 'text/x-python',
    'etx': 'text/x-setext',
    'sgm': 'text/x-sgml',
    'sgml': 'text/x-sgml',
    'vcf': 'text/x-vcard',
    'xml': 'text/xml',
    'mp4': 'video/mp4',
    'mpeg': 'video/mpeg',
    'm1v': 'video/mpeg',
    'mpa': 'video/mpeg',
    'mpe': 'video/mpeg',
    'mpg': 'video/mpeg',
    'mov': 'video/quicktime',
    'qt': 'video/quicktime',
    'webm': 'video/webm',
    'avi': 'video/x-msvideo',
    'movie': 'video/x-sgi-movie',
}


def manage_files(request, allow_dirs=True):
    path = '.' + request.path
    ext = path.split('.', -1)[-1]
    if os.path.isdir(path) and allow_dirs:
        return list_directory(path)
    if os.path.isfile(path):
        if ext in types.keys():
            return sbeaver.open_file(path, types[ext], path[2:])
        else:
            return sbeaver.open_file(path, "application/octet-stream", path[2:])
    return 500, 'error, unknown type'


def list_directory(path):
    """Helper to produce a directory listing (absent index.html).

    Return value is either a file object, or None (indicating an
    error).  In either case, the headers are sent, making the
    interface the same as for send_head().

    """
    # try:
    list = os.listdir(path)
    # except OSError as e:
    #    print_tb(e.__traceback__)
    #    return pnf()
    list.sort(key=lambda a: a.lower())
    r = []
    try:
        display_path = urllib.parse.unquote(path,
                                            errors='surrogatepass')
    except UnicodeDecodeError:
        display_path = urllib.parse.unquote(path)
    display_path = html.escape(display_path, quote=False)
    enc = sys.getfilesystemencoding()
    title = 'Directory listing for %s' % display_path
    r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
             '"http://www.w3.org/TR/html4/strict.dtd">')
    r.append('<html>\n<head>')
    r.append('<meta http-equiv="Content-Type" '
             'content="text/html; charset=%s">' % enc)
    r.append('<title>%s</title>\n</head>' % title)
    r.append('<body>\n<h1>%s</h1>' % title)
    r.append('<hr>\n<ul>')
    for name in list:
        fullname = os.path.join(path, name)
        display_name = link_name = name
        # Append / for directories or @ for symbolic links
        if os.path.isdir(fullname):
            display_name = name + "/"
            link_name = name + "/"
        if os.path.islink(fullname):
            display_name = name + "@"
            # Note: a link to a directory displays with @ and links with /
        r.append('<li><a href="%s">%s</a></li>'
                 % (urllib.parse.quote(link_name,
                                       errors='surrogatepass'),
                    html.escape(display_name, quote=False)))
    r.append('</ul>\n<hr>\n</body>\n</html>\n')
    encoded = '\n'.join(r).encode(enc, 'surrogateescape')
    f = io.BytesIO()
    f.write(encoded)
    f.seek(0)
    return 200, f.read(-1), sbeaver.Types.Text.html, {"Content-type": "text/html; charset=%s" % enc,
                                                      "Content-Length": str(len(encoded))}
