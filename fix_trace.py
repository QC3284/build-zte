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

# ---- f2fs/xattr.c: remove unused sbi in __f2fs_setxattr ----
p = 'fs/f2fs/xattr.c'
s = open(p).read()
old = 'static int __f2fs_setxattr(struct inode *inode, int index,'
k = s.find(old)
if k > 0:
    j = s.find('{', k) + 1
    m = s.find('struct f2fs_sb_info *sbi = F2FS_I_SB(inode);', j)
    if 0 < m < j + 200:
        e = s.find('\n', m) + 1
        s = s[:m] + s[e:]
        open(p, 'w').write(s)
        print('xattr unused sbi removed')

# ---- drivers/block/loop.c: remove unused bdev in loop_set_status ----
p = 'drivers/block/loop.c'
s = open(p).read()
k = s.find('static int\nloop_set_status(struct loop_device *lo, const struct loop_info64 *info)')
if k > 0:
    j = s.find('{', k) + 1
    m = s.find('\tstruct block_device *bdev;', j)
    if 0 < m < j + 300:
        e = s.find('\n', m) + 1
        s = s[:m] + s[e:]
        open(p, 'w').write(s)
        print('loop.c bdev removed')

# ---- drivers/interconnect/internal.h: add bool enabled to icc_req ----
p = 'drivers/interconnect/internal.h'
s = open(p).read()
old = '\tu32 tag;\n\tu32 avg_bw;\n\tu32 peak_bw;\n};'
new = '\tu32 tag;\n\tu32 avg_bw;\n\tu32 peak_bw;\n\tbool enabled;\n};'
if old in s:
    open(p, 'w').write(s.replace(old, new, 1))
    print('icc enabled added')

# ---- netdevice.h: DEV_STATS macros must use non-prefixed fields (Android struct) ----
p = 'include/linux/netdevice.h'
s = open(p).read()
s = s.replace('atomic_long_inc(&(DEV)->stats.__##FIELD)', 'atomic_long_inc(&(DEV)->stats.FIELD)')
s = s.replace('atomic_long_add((VAL), &(DEV)->stats.__##FIELD)', 'atomic_long_add((VAL), &(DEV)->stats.FIELD)')
s = s.replace('atomic_long_read(&(DEV)->stats.__##FIELD)', 'atomic_long_read(&(DEV)->stats.FIELD)')
open(p, 'w').write(s)
print('netdevice macros fixed')

# ---- netdevice.h: plain ops for Android's non-atomic stats fields ----
p = 'include/linux/netdevice.h'
s = open(p).read()
s = s.replace('atomic_long_inc(&(DEV)->stats.FIELD)', '(DEV)->stats.FIELD++')
s = s.replace('atomic_long_add((VAL), &(DEV)->stats.FIELD)', '(DEV)->stats.FIELD += (VAL)')
s = s.replace('atomic_long_read(&(DEV)->stats.FIELD)', '(DEV)->stats.FIELD')
open(p, 'w').write(s)
print('netdevice plain ops')
