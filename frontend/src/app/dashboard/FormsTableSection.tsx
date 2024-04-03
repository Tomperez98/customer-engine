import Table from '@/components/table/Table'
import useGetForms from '@/hooks/forms/useGetForms'
import {createColumnHelper, Row} from '@tanstack/react-table'
import {Form, FormKeys} from '@/types/Forms'
import Link from 'next/link'
import {useMemo, useEffect, useState} from 'react'
import useDeleteForm from '@/hooks/forms/useDeleteForm'
import IconButton from '@/components/IconButton'
import {MdDelete, MdInfo} from 'react-icons/md'
import CallToAction from '@/components/CallToAction'
import ClipLoader from 'react-spinners/ClipLoader'
import DeleteConfirmationModal from '@/components/modal/DeleteConfirmationModal'
import {cyan400} from '@/constants/colors'
import FormCreationModal from './FormCreationModal'
import {MdAddCircle} from 'react-icons/md'

const FormsTableSection: React.FC = () => {
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState<boolean>(false)
    const [isCreateModalOpen, setIsCreateModalOpen] = useState<boolean>(false)
    const [deleteFormId, setDeleteFormId] = useState<string>('')
    const {data, isLoading, refetch} = useGetForms()
    const forms = useMemo(() => data?.automatic_response, [data])
    const {deleteForm} = useDeleteForm()
    const [shouldRefetch, setShouldRefetch] = useState<boolean>(false)

    const handleTriggerDeleteModal = (formId: string) => {
        setDeleteFormId(formId)
        setIsDeleteModalOpen(true)
    }

    const handleDeleteForm = async (id: string) => {
        setIsDeleteModalOpen(false)
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
                            tooltip='Detalles'
                            size='text-lg'
                        />
                    </Link>
                    <IconButton
                        fill='text-red-500'
                        Icon={MdDelete}
                        tooltip='Borrar'
                        onClick={() =>
                            handleTriggerDeleteModal(
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
        <>
            <FormCreationModal
                isOpen={isCreateModalOpen}
                setIsOpen={setIsCreateModalOpen}
                setShouldRefetch={setShouldRefetch}
            />

            <DeleteConfirmationModal
                deleteAction={() => handleDeleteForm(deleteFormId)}
                elementName='formulario'
                isOpen={isDeleteModalOpen}
                setIsOpen={setIsDeleteModalOpen}
            />

            <section className='w-full'>
                <div className='mb-4 flex items-center gap-2'>
                    <h1 className='pb-1 text-3xl font-extrabold text-neutral-800'>
                        Formularios
                    </h1>
                    <IconButton
                        size='text-xl'
                        tooltip='Crear formulario'
                        onClick={() => setIsCreateModalOpen(true)}
                        Icon={MdAddCircle}
                    />
                    {isLoading && <ClipLoader color={cyan400} size={18} />}
                </div>
                {isLoading && (
                    <div className='flex h-64 items-center justify-center'>
                        <ClipLoader color={cyan400} size={50} />{' '}
                    </div>
                )}
                {!isLoading && (forms as Form[])?.length > 0 && (
                    <Table columns={columns} data={forms as Form[]} />
                )}
                {!isLoading && (forms as Form[])?.length === 0 && (
                    <div className='box-border flex w-full flex-col gap-4 rounded-md bg-white p-8 shadow-md'>
                        <CallToAction
                            actionLabel='Crear formulario'
                            onClick={() => setIsCreateModalOpen(true)}
                            text='Aún no tienes formularios.'
                        />
                    </div>
                )}
            </section>
        </>
    )
}

export default FormsTableSection
