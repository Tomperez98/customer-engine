import IconButton from '@/components/IconButton'
import {cyan400} from '@/constants/colors'
import {useMemo, useState} from 'react'
import {MdCheckCircle} from 'react-icons/md'
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

const UnmatchedPromptsSection = () => {
    const [selectedForm, setSelectedForm] = useState<string>()
    const [rowSelection, setRowSelection] = useState({})
    const {data} = useGetUnmatchedPrompts()
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
            cell: (info) => info.getValue(),
        }),
    ]
    const selectedRowsIds = useMemo(() => {
        const selectedRows = unmatchedPrompts.filter(
            (_: UnmatchedPrompt, key: number) =>
                Object.keys(rowSelection).includes(String(key))
        )
        return selectedRows.map((row: UnmatchedPrompt) => row.prompt_id)
    }, [rowSelection, unmatchedPrompts])

    return (
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
                        onClick={() => null}
                        Icon={MdCheckCircle}
                        disabled={selectedRowsIds.length === 0 || !selectedForm}
                    />
                    <ClipLoader color={cyan400} size={18} />
                </div>
            </div>
            <Table
                columns={columns}
                data={unmatchedPrompts}
                rowSelection={rowSelection}
                setRowSelection={setRowSelection}
            />
        </section>
    )
}

export default UnmatchedPromptsSection
