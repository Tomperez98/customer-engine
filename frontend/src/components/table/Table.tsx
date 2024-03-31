import {
    useReactTable,
    flexRender,
    ColumnDef,
    getCoreRowModel,
} from '@tanstack/react-table'

interface TableProps<T> {
    columns: ColumnDef<T, string>[]
    data: T[]
}

const Table = <T extends {}>({columns, data}: TableProps<T>) => {
    const table = useReactTable<T>({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
    })

    return (
        <table className='w-full rounded-lg bg-white px-2 text-left text-gray-600 shadow-sm'>
            <thead className='border-b border-slate-200 text-sm shadow-sm'>
                {table.getHeaderGroups().map((headerGroup) => (
                    <tr key={headerGroup.id}>
                        {headerGroup.headers.map((header) => (
                            <th
                                key={header.id}
                                className='px-4 py-2 capitalize'>
                                {header.isPlaceholder
                                    ? null
                                    : flexRender(
                                          header.column.columnDef.header,
                                          header.getContext()
                                      )}
                            </th>
                        ))}
                    </tr>
                ))}
            </thead>
            <tbody className='text-sm'>
                {table.getRowModel().rows.map((row, idx) => (
                    <tr className='border-b border-slate-200' key={row.id}>
                        {row.getVisibleCells().map((cell) => (
                            <td key={cell.id} className='px-4 py-2'>
                                {flexRender(
                                    cell.column.columnDef.cell,
                                    cell.getContext()
                                )}
                            </td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    )
}

export default Table
