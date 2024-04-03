'use client'

import Button from '@/components/Button'
import EditableListField from '@/components/EditableListField'
import Modal from '@/components/modal/Modal'
import useCreateExamples from '@/hooks/examples/useCreateExamples'
import {
    validateAllEmptyFields,
    validateNoEmptyFields,
} from '@/utils/validateExamples'
import {useEffect, useState} from 'react'

interface AddExamplesProps {
    formId: string
    isOpen: boolean
    setIsOpen: (isOpen: boolean) => void
    setShouldRefetch: (shouldRefetch: boolean) => void
}

const AddExamples = ({
    formId,
    isOpen,
    setIsOpen,
    setShouldRefetch,
}: AddExamplesProps) => {
    const [examples, setExamples] = useState<string[]>([''])
    const {submit} = useCreateExamples(formId, examples)

    const handleAddExamples = async () => {
        await submit()
        setShouldRefetch(true)
        setIsOpen(false)
    }

    useEffect(() => {
        if (!isOpen) {
            setExamples([''])
        }
    }, [isOpen])

    return (
        <Modal isOpen={isOpen} setIsOpen={setIsOpen}>
            <div className='w-[50vw]'>
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
        </Modal>
    )
}

export default AddExamples
