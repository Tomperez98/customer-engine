import IconButton from '@/components/IconButton'
import {cyan400} from '@/constants/colors'
import {useEffect, useMemo, useState} from 'react'
import {MdCheckCircle, MdDelete} from 'react-icons/md'
import {ClipLoader} from 'react-spinners'
import {
    createColumnHelper,
    Row,
    Table as TableType,
} from '@tanstack/react-table'
import {UnmatchedPrompt, UnmatchedPromptsKeys} from '@/types/UnmatchedPrompts'
import useGetUnmatchedPrompts from '@/hooks/unmatched-propmts/useGetUnmatchedPrompts'
import Table from '@/components/table/Table'
import Dropdown from '@/components/Dropdown'
import useGetForms from '@/hooks/forms/useGetForms'
import {convertToDropdownOption} from '@/utils/convertToDropdownOption'
import {Form} from '@/types/Forms'
import IndeterminateCheckbox from '@/components/table/IndeterminateCheckbox'
import usePostUnmatchedPromptsToForm from '@/hooks/unmatched-propmts/usePostUnmatchedPromptsToForm'
import DeleteConfirmationModal from '@/components/modal/DeleteConfirmationModal'
import useDeleteUnmatchedPrompts from '@/hooks/unmatched-propmts/useDeleteUnmatchedPrompts'
import {formatDate} from '@/utils/formatDate'

const UnmatchedPromptsSection = () => {
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState<boolean>(false)
    const [selectedForm, setSelectedForm] = useState<string>()
    const [rowSelection, setRowSelection] = useState({})
    const [shouldRefetch, setShouldRefetch] = useState<boolean>(false)
    const {submit} = usePostUnmatchedPromptsToForm()
    const {submit: submitDelete} = useDeleteUnmatchedPrompts()
    const {data, isLoading, refetch} = useGetUnmatchedPrompts()
    const unmatchedPrompts = useMemo(
        () => data?.unmatched_prompts || [],
        [data]
    )
    const {data: formsData} = useGetForms()
    const forms = (formsData?.automatic_response as Form[]) || []
    const dropdownOptions = forms.map((form) =>
        convertToDropdownOption(form.automatic_response_id, form.name)
    )

    const columnHelper = createColumnHelper<UnmatchedPrompt>()
    const columns = [
        {
            id: 'select',
            header: ({table}: {table: TableType<UnmatchedPrompt>}) => (
                <IndeterminateCheckbox
                    {...{
                        checked: table.getIsAllRowsSelected(),
                        indeterminate: table.getIsSomeRowsSelected(),
                        onChange: table.getToggleAllRowsSelectedHandler(),
                    }}
                />
            ),
            cell: ({row}: {row: Row<UnmatchedPrompt>}) => (
                <div className='px-1'>
                    <IndeterminateCheckbox
                        {...{
                            checked: row.getIsSelected(),
                            disabled: !row.getCanSelect(),
                            indeterminate: row.getIsSomeSelected(),
                            onChange: row.getToggleSelectedHandler(),
                        }}
                    />
                </div>
            ),
        },
        columnHelper.accessor('prompt_id', {
            header: () => <span>{UnmatchedPromptsKeys['prompt_id']}</span>,
            cell: (info) => info.getValue(),
        }),
        columnHelper.accessor('prompt', {
            header: () => <span>{UnmatchedPromptsKeys['prompt']}</span>,
            cell: (info) => info.getValue(),
        }),
        columnHelper.accessor('created_at', {
            header: () => <span>{UnmatchedPromptsKeys['created_at']}</span>,
            cell: (info) => formatDate(info.getValue()),
        }),
    ]
    const selectedRowsIds = useMemo(() => {
        const selectedRows = unmatchedPrompts.filter(
            (_: UnmatchedPrompt, key: number) =>
                Object.keys(rowSelection).includes(String(key))
        )
        return selectedRows.map((row: UnmatchedPrompt) => row.prompt_id)
    }, [rowSelection, unmatchedPrompts])

    const handleAddUnmatchedPromptToForm = async () => {
        await submit({
            prompt_ids: selectedRowsIds,
            automatic_response_id: selectedForm!,
        })
        setRowSelection({})
        setShouldRefetch(true)
    }

    const handleDeleteUnmatchedPrompts = async () => {
        await submitDelete({
            prompt_ids: selectedRowsIds,
        })
        setRowSelection({})
        setShouldRefetch(true)
        setIsDeleteModalOpen(false)
    }

    useEffect(() => {
        if (shouldRefetch) {
            refetch()
            setShouldRefetch(false)
        }
    }, [shouldRefetch])

    return (
        <>
            <DeleteConfirmationModal
                deleteAction={handleDeleteUnmatchedPrompts}
                elementName='mensajes'
                isOpen={isDeleteModalOpen}
                setIsOpen={setIsDeleteModalOpen}
            />
            <section>
                <h1 className='mb-4 pb-1 text-3xl font-extrabold text-neutral-800'>
                    Mensajes sin formulario
                </h1>
                <div className='mb-4'>
                    <h2 className='mb-2 pb-1 text-xl font-extrabold text-neutral-800'>
                        Agregar a formulario:
                    </h2>
                    <div className='flex flex-row items-center gap-2'>
                        <Dropdown
                            options={dropdownOptions}
                            onSelect={setSelectedForm}
                            placeholderText='Selecciona un formulario'
                        />
                        <IconButton
                            size='text-xl'
                            tooltip='Confirmar'
                            onClick={handleAddUnmatchedPromptToForm}
                            Icon={MdCheckCircle}
                            disabled={
                                selectedRowsIds.length === 0 || !selectedForm
                            }
                        />
                        <IconButton
                            size='text-xl'
                            tooltip='Borrar seleccionados'
                            fill='text-red-500 disabled:text-gray-200'
                            onClick={() => setIsDeleteModalOpen(true)}
                            Icon={MdDelete}
                            disabled={selectedRowsIds.length === 0}
                        />
                        {isLoading && <ClipLoader color={cyan400} size={18} />}
                    </div>
                </div>
                {!isLoading && unmatchedPrompts?.length > 0 && (
                    <Table
                        columns={columns}
                        data={unmatchedPrompts}
                        rowSelection={rowSelection}
                        setRowSelection={setRowSelection}
                    />
                )}
                {!isLoading && unmatchedPrompts?.length === 0 && (
                    <div className='box-border flex w-full justify-center gap-4 rounded-md bg-white p-8 shadow-md'>
                        <p>
                            No tienes mensajes que no pertenezcan a ningun
                            formulario.
                        </p>
                    </div>
                )}
            </section>
        </>
    )
}

export default UnmatchedPromptsSection
