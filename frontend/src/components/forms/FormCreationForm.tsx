'use client'

import {FORM_TEMPLATE, FORM_FIELDS} from '@/constants/formFields'
import {ChangeEvent, useCallback} from 'react'
import {FormTemplate, FormKey} from '@/types/Forms'
import {InputField, InputName} from '@/types/Inputs'
import {
    validateAllEmptyFields,
    validateNoEmptyFields,
} from '@/utils/validateFormFields'

import RichTextEditor from '@/components/RichTextEditor'
import Input from '@/components/Input'
import Button from '@/components/Button'

interface FormCreationFormProps {
    createAction: () => void
    formTemplate: FormTemplate
    setFormTemplate: (formTemplate: FormTemplate) => void
}

const FormCreationForm = ({
    createAction,
    formTemplate,
    setFormTemplate,
}: FormCreationFormProps) => {
    const handleFormFieldChange = useCallback(
        (
            event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
            name: InputName
        ) => {
            setFormTemplate({
                ...formTemplate,
                [name]: event.target.value,
            })
        },
        [formTemplate, setFormTemplate]
    )

    const getInputElement = useCallback(
        (field: InputField, idx: number) => {
            const {name, component, label} = field

            if (component === 'input') {
                return (
                    <div key={idx} className='flex flex-col'>
                        <label
                            htmlFor={name}
                            className='mb-2 text-lg font-semibold capitalize text-neutral-800'>
                            {label}
                        </label>
                        <Input
                            name={name as FormKey}
                            onChange={handleFormFieldChange}
                            value={formTemplate[name as FormKey] || ''}
                        />
                    </div>
                )
            }
            if (component === 'textarea') {
                return (
                    <div key={idx} className='flex flex-col'>
                        <label
                            htmlFor={name}
                            className='mb-2 text-lg font-semibold capitalize text-neutral-800'>
                            {label}
                        </label>
                        <RichTextEditor
                            name={name as FormKey}
                            onChange={handleFormFieldChange}
                            value={formTemplate[name as FormKey] || ''}
                            formTemplate={formTemplate}
                            setFormTemplate={setFormTemplate}
                        />
                    </div>
                )
            }
            return null
        },
        [formTemplate, handleFormFieldChange]
    )

    return (
        <>
            {FORM_FIELDS.map((field, idx) => {
                return getInputElement(field, idx)
            })}
            <div className='mt-4 flex w-full flex-row items-center justify-end gap-4'>
                <Button
                    label='Descartar'
                    onClick={() => setFormTemplate(FORM_TEMPLATE)}
                    style='secondary'
                    disabled={validateAllEmptyFields(formTemplate)}
                />
                <Button
                    disabled={!validateNoEmptyFields(formTemplate)}
                    label='Guardar'
                    onClick={createAction}
                />
            </div>
        </>
    )
}

export default FormCreationForm
