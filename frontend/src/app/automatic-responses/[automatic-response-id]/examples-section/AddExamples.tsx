'use client'

import Button from '@/components/Button'
import EditableListField from '@/components/EditableListField'
import useCreateExamples from '@/hooks/examples/useCreateExamples'
import {
    validateAllEmptyFields,
    validateNoEmptyFields,
} from '@/utils/validateExamples'
import {useState} from 'react'

interface AddExamplesProps {
    formId: string
    setShouldRefetch: (shouldRefetch: boolean) => void
}

const AddExamples = ({formId, setShouldRefetch}: AddExamplesProps) => {
    const [examples, setExamples] = useState<string[]>([''])
    const {submit} = useCreateExamples(formId, examples)

    const handleAddExamples = async () => {
        await submit()
        setShouldRefetch(true)
    }

    return (
        <div>
            <EditableListField
                label='Agregar Ejemplos'
                listValues={examples}
                setListValues={setExamples}
                editableOnly
            />
            <div className='mt-4 flex w-full flex-row items-center justify-end gap-4'>
                <Button
                    label='Descartar'
                    onClick={() => setExamples([''])}
                    style='secondary'
                    disabled={
                        validateAllEmptyFields(examples) &&
                        examples.length === 1
                    }
                />
                <Button
                    disabled={!validateNoEmptyFields(examples)}
                    label='Guardar'
                    onClick={handleAddExamples}
                />
            </div>
        </div>
    )
}

export default AddExamples
