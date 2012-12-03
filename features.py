import tables

def store_ref_data(filename, pos, x1, y1, x2, y2, frames):
    f = tables.openFile('reference_data.hdf', 'a')
    try:
        features = f.root.features
    except tables.NoSuchNodeError:
        schema = {
            'filename':  tables.StringCol(100),
            'pos':      tables.IntCol(),
            'x1':      tables.IntCol(),
            'y1':      tables.IntCol(),
            'x2':      tables.IntCol(),
            'y2':      tables.IntCol(),
            }
        f.createTable('/', 'features', schema)
        features = f.root.features

    id = len(features)
    row = features.row
    row['filename'] = filename
    row['pos'] = pos
    row['x1'] = x1
    row['y1'] = y1
    row['x2'] = x2
    row['y2'] = y2
    row.append()

    features.flush()

    try:
        f.root.frame_arrays
    except tables.NoSuchNodeError:
        f.createGroup(f.root, 'frame_arrays')

    f.createArray('/frame_arrays', 'array%d' % id, frames)
    f.close()


if __name__ == '__main__':
    store_ref_data('test.avi',666,10,10,100,100, [0,1,2,3,4])

