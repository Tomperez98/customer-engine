import {ChangeEvent, useMemo, useState} from 'react'
import {createColumnHelper, Row} from '@tanstack/react-table'
import {Example, ExampleKeys} from '@/types/Examples'
import Table from '@/components/table/Table'
import IconButton from '@/components/IconButton'
import {MdDelete, MdEditSquare} from 'react-icons/md'
import useDeleteExample from '@/hooks/examples/useDeleteExample'
import {ExampleResponse} from '@/hooks/examples/useGetExamples'
import EditableCell from '@/components/table/EditableCell'
import useEditExample from '@/hooks/examples/useEditExample'
import DeleteConfirmationModal from '@/components/modal/DeleteConfirmationModal'
import {cyan400} from '@/constants/colors'
import {ClipLoader} from 'react-spinners'

interface ExamplesTableProps {
    data: ExampleResponse
    formId: string
    setShouldRefetch: (shouldRefetch: boolean) => void
}

const ExamplesTable = ({
    data,
    formId,
    setShouldRefetch,
}: ExamplesTableProps) => {
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState<boolean>(false)
    const [deleteExampleId, setDeleteExampleId] = useState<string>('')
    const examples = useMemo(() => data?.examples, [data])
    const {deleteExample} = useDeleteExample()
    const {editExample, isLoading} = useEditExample(formId)
    const [editingFields, setEditingFields] = useState<
        {id: string; example: string}[]
    >([])
    const handleDeleteExample = async (formId: string, exampleId: string) => {
        setIsDeleteModalOpen(false)
        await deleteExample(formId, exampleId)
        setShouldRefetch(true)
    }

    const getEditingField = (exampleId: string) =>
        editingFields.find((example) => example.id === exampleId)

    const handleEditExample = async (exampleId: string, data: string) => {
        await editExample(exampleId, data)
        setShouldRefetch(true)
    }

    const handleTriggerDeleteModal = (exampleId: string) => {
        setDeleteExampleId(exampleId)
        setIsDeleteModalOpen(true)
    }

    const columnHelper = createColumnHelper<Example>()
    const columns = [
        columnHelper.accessor('example_id', {
            header: () => <span>{ExampleKeys['example_id']}</span>,
            cell: (info) => info.getValue(),
        }),
        columnHelper.accessor('example', {
            header: () => <span>{ExampleKeys['example']}</span>,
            cell: (info) => (
                <div className='w-64'>
                    {getEditingField(info.row.getValue('example_id')) ? (
                        <EditableCell
                            initialValue={
                                getEditingField(info.row.getValue('example_id'))
                                    ?.example || ''
                            }
                            onCancel={() =>
                                setEditingFields(
                                    editingFields.filter(
                                        (example) =>
                                            example.id !==
                                            info.row.getValue('example_id')
                                    )
                                )
                            }
                            onSubmit={(newValue) => {
                                handleEditExample(
                                    info.row.getValue('example_id'),
                                    newValue
                                )
                                setEditingFields(
                                    editingFields.filter(
                                        (example) =>
                                            example.id !==
                                            info.row.getValue('example_id')
                                    )
                                )
                            }}
                        />
                    ) : (
                        <span>
                            {isLoading ? (
                                <ClipLoader color={cyan400} size={18} />
                            ) : (
                                info.getValue()
                            )}
                        </span>
                    )}
                </div>
            ),
        }),
        {
            id: 'actions',
            header: () => null,
            cell: ({row}: {row: Row<Example>}) => (
                <div className='flex flex-row items-center gap-4'>
                    <IconButton
                        Icon={MdEditSquare}
                        tooltip='Editar'
                        onClick={() =>
                            setEditingFields([
                                ...editingFields,
                                {
                                    id: row.getValue('example_id'),
                                    example: row.getValue('example'),
                                },
                            ])
                        }
                        size='text-lg'
                    />
                    <IconButton
                        fill='text-red-500'
                        Icon={MdDelete}
                        tooltip='Borrar'
                        onClick={() =>
                            handleTriggerDeleteModal(row.getValue('example_id'))
                        }
                        size='text-lg'
                    />
                </div>
            ),
        },
    ]

    return (
        <>
            <DeleteConfirmationModal
                deleteAction={() =>
                    handleDeleteExample(formId, deleteExampleId)
                }
                elementName='ejemplo'
                isOpen={isDeleteModalOpen}
                setIsOpen={setIsDeleteModalOpen}
            />
            <Table columns={columns} data={examples} />
        </>
    )
}

export default ExamplesTable
