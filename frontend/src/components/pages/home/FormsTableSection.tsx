import Table from '@/components/Table'
import useGetForms from '@/hooks/useGetForms'
import {createColumnHelper, Row} from '@tanstack/react-table'
import {Form, FormKeys} from '@/types/Forms'
import Link from 'next/link'
import {useMemo, useEffect, useState} from 'react'
import {FaMagnifyingGlass, FaTrash} from 'react-icons/fa6'
import useDeleteForm from '@/hooks/useDeleteForm'

const FormsTableSection: React.FC = () => {
    const {data, isLoading, refetch} = useGetForms()
    const forms = useMemo(() => data?.automatic_response, [data])
    const {deleteForm} = useDeleteForm()
    const [shouldRefetch, setShouldRefetch] = useState<boolean>(false)

    const handleDeleteForm = async (id: string) => {
        await deleteForm(id)
        setShouldRefetch(true)
    }

    const columnHelper = createColumnHelper<Form>()
    const columns = [
        columnHelper.accessor('automatic_response_id', {
            header: () => <span>{FormKeys['automatic_response_id']}</span>,
            cell: (info) => info.getValue(),
        }),
        columnHelper.accessor('name', {
            header: () => <span>{FormKeys['name']}</span>,
            cell: (info) => info.getValue(),
        }),
        {
            id: 'actions',
            header: () => null,
            cell: ({row}: {row: Row<Form>}) => (
                <div className='flex flex-row gap-4'>
                    <Link
                        href={`/automatic-responses/${row.getValue('automatic_response_id')}`}
                        target='_blank'>
                        <FaMagnifyingGlass color='#455d7a' />
                    </Link>
                    <div className='cursor-pointer'>
                        <FaTrash
                            onClick={() =>
                                handleDeleteForm(
                                    row.getValue('automatic_response_id')
                                )
                            }
                            color='#f95959'
                        />
                    </div>
                </div>
            ),
        },
    ]

    useEffect(() => {
        if (shouldRefetch) {
            refetch()
            setShouldRefetch(false)
        }
    }, [shouldRefetch])

    return (
        <section className='w-full'>
            <h2 className='mb-4 text-3xl font-extrabold text-slate-800'>
                Formularios
            </h2>

            {forms && <Table columns={columns} data={forms as Form[]} />}
        </section>
    )
}

export default FormsTableSection
