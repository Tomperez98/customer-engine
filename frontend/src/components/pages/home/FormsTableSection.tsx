import Table from '@/components/Table'
import useGetForms from '@/hooks/forms/useGetForms'
import {createColumnHelper, Row} from '@tanstack/react-table'
import {Form, FormKeys} from '@/types/Forms'
import Link from 'next/link'
import {useMemo, useEffect, useState} from 'react'
import useDeleteForm from '@/hooks/forms/useDeleteForm'
import IconButton from '@/components/IconButton'
import {MdDelete, MdInfo} from 'react-icons/md'

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
                <div className='flex flex-row items-center gap-4'>
                    <Link
                        className='flex items-center'
                        href={`/automatic-responses/${row.getValue('automatic_response_id')}`}
                        target='_blank'>
                        <IconButton
                            Icon={MdInfo}
                            onClick={() => null}
                            size='text-lg'
                        />
                    </Link>
                    <IconButton
                        fill='text-red-500'
                        Icon={MdDelete}
                        onClick={() =>
                            handleDeleteForm(
                                row.getValue('automatic_response_id')
                            )
                        }
                        size='text-lg'
                    />
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
            <h1 className='mb-4 text-3xl font-extrabold text-neutral-800'>
                Formularios
            </h1>

            {forms && <Table columns={columns} data={forms as Form[]} />}
        </section>
    )
}

export default FormsTableSection
