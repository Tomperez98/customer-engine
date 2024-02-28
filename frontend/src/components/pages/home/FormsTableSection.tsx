'use client'
import Table from '@/components/Table'
import useGetForms from '@/hooks/useGetForms'
import {createColumnHelper, Row} from '@tanstack/react-table'
import {Form, FormKeys} from '@/types/Forms'
import Link from 'next/link'
import {useMemo} from 'react'
import {FaMagnifyingGlass} from 'react-icons/fa6'
import {FaTrash} from 'react-icons/fa6'
import useDeleteForm from '@/hooks/useDeleteForm'

const FormsTableSection: React.FC = () => {
    const {data, isLoading} = useGetForms()
    const forms = useMemo(() => data?.automatic_response, [data])
    const {deleteForm} = useDeleteForm()
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
            cell: ({row}: {row: Row<Form>}) => {
                return (
                    <div className='flex flex-row gap-4'>
                        <Link
                            href={`/automatic-responses/${row.getValue('automatic_response_id')}`}
                            target='_blank'>
                            <FaMagnifyingGlass color='#455d7a' />
                        </Link>
                        <FaTrash
                            onClick={async () =>
                                deleteForm(
                                    row.getValue('automatic_response_id')
                                )
                            }
                            color='#f95959'
                        />
                    </div>
                )
            },
        },
    ]
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
