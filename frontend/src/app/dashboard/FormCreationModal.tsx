'use client'
import FormCreationForm from '@/components/forms/FormCreationForm'
import Modal from '@/components/modal/Modal'
import {useCallback, useState} from 'react'
import {FormTemplate} from '@/types/Forms'
import {FORM_TEMPLATE} from '@/constants/formFields'
import useCreateForm from '@/hooks/forms/useCreateForm'

interface FormCreationModalProps {
    isOpen: boolean
    setIsOpen: (isOpen: boolean) => void
    setShouldRefetch: (shouldRefetch: boolean) => void
}

const FormCreationModal = ({
    isOpen,
    setIsOpen,
    setShouldRefetch,
}: FormCreationModalProps) => {
    const [formTemplate, setFormTemplate] =
        useState<FormTemplate>(FORM_TEMPLATE)
    const {submit} = useCreateForm(formTemplate)

    const handleCreateForm = useCallback(async () => {
        await submit()
        setShouldRefetch(true)
        setIsOpen(false)
    }, [submit])

    return (
        <Modal isOpen={isOpen} setIsOpen={setIsOpen}>
            <div className='flex w-[50vw]  flex-col gap-4 bg-white p-8'>
                <h3 className='mb-4 text-3xl font-extrabold text-neutral-800'>
                    Crear formulario
                </h3>
                <FormCreationForm
                    createAction={handleCreateForm}
                    formTemplate={formTemplate}
                    setFormTemplate={setFormTemplate}
                />
            </div>
        </Modal>
    )
}

export default FormCreationModal
