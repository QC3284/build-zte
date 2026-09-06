import sys
p = 'kernel/trace/trace.c'
s = open(p).read()
broken = '''\tmutex_lock(&event_mutex);

\t/* Fail if the file is marked for removal */
\tif (file->flags & EVENT_FILE_FL_FREED) {
\t\ttrace_array_put(file->tr);
\t\tret = -ENODEV;
\t} else {
\t\tevent_file_get(file);
\t}

\tmutex_unlock(&event_mutex);
\tif (ret)
\t\treturn ret;

\tfilp->private_data = inode->i_private;'''
fixed = '''\tfilp->private_data = inode->i_private;'''
assert broken in s, 'generic_tr block not found'
s = s.replace(broken, fixed, 1)
anchor = '''\tret = tracing_check_open_get_tr(file->tr);
\tif (ret)
\t\treturn ret;

\tfilp->private_data = inode->i_private;'''
repl = '''\tret = tracing_check_open_get_tr(file->tr);
\tif (ret)
\t\treturn ret;

\tmutex_lock(&event_mutex);

\t/* Fail if the file is marked for removal */
\tif (file->flags & EVENT_FILE_FL_FREED) {
\t\ttrace_array_put(file->tr);
\t\tret = -ENODEV;
\t} else {
\t\tevent_file_get(file);
\t}

\tmutex_unlock(&event_mutex);
\tif (ret)
\t\treturn ret;

\tfilp->private_data = inode->i_private;'''
assert anchor in s, 'file_tr anchor not found'
s = s.replace(anchor, repl, 1)
open(p, 'w').write(s)
print('trace.c fixed' if 'EVENT_FILE_FL_FREED' in s else 'FAILED')
# ---- f2fs/xattr.c: restore sbi declaration in read_inline_xattr ----
p = 'fs/f2fs/xattr.c'
s = open(p).read()
old = 'static int read_inline_xattr(struct inode *inode, struct page *ipage,'
k = s.find(old)
if k > 0 and 'struct f2fs_sb_info *sbi' not in s[k:k+300]:
    j = s.find('{', k) + 1
    s = s[:j] + '\n\tstruct f2fs_sb_info *sbi = F2FS_SB(inode->i_sb);' + s[j:]
    open(p, 'w').write(s)
    print('xattr.c fixed')
else:
    print('xattr.c already ok')
