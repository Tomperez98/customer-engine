'use client'

import EditableListField from '@/components/EditableListField'
import Layout from '@/components/layout'
import {FORM_TEMPLATE, INPUT_FIELDS} from '@/constants/formFields'
import useCreateForm from '@/hooks/forms/useCreateForm'
import {ChangeEvent, useCallback, useEffect, useState} from 'react'
import {FormTemplate, FormKey, InputField} from '@/types/Forms'
import {redirect} from 'next/navigation'
import {
    validateAllEmptyFields,
    validateNoEmptyFields,
} from '@/utils/validateFormFields'

import RichTextEditor from '@/components/RichTextEditor'
import Input from '@/components/Input'
import Button from '@/components/Button'

const CreateForm = () => {
    const [formTemplate, setFormTemplate] =
        useState<FormTemplate>(FORM_TEMPLATE)
    const [shouldRedirect, setShouldRedirect] = useState<boolean>(false)
    const {submit} = useCreateForm(formTemplate)
    const handleInputFieldChange = useCallback(
        (
            event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
            name: FormKey
        ) => {
            setFormTemplate((prevState) => ({
                ...prevState,
                [name]: event.target.value,
            }))
        },
        []
    )

    const handleCreateForm = useCallback(async () => {
        await submit()
        setShouldRedirect(true)
    }, [submit])

    useEffect(() => {
        if (shouldRedirect) {
            redirect('/dashboard')
        }
    }, [shouldRedirect])

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
                            name={name}
                            onChange={handleInputFieldChange}
                            value={formTemplate[name] || ''}
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
                            name={name}
                            onChange={handleInputFieldChange}
                            value={formTemplate[name] || ''}
                            formTemplate={formTemplate}
                            setFormTemplate={setFormTemplate}
                        />
                    </div>
                )
            }
            if (component === 'list') {
                return (
                    <EditableListField
                        templateForm={formTemplate}
                        setTemplateForm={setFormTemplate}
                        key={idx}
                        fieldName={name}
                        label={label}
                        originalValue={formTemplate[name] || []}
                        editableOnly
                    />
                )
            }
            return null
        },
        [formTemplate, handleInputFieldChange]
    )

    return (
        <Layout>
            <section className='flex flex-col'>
                <h1 className='mb-4 text-3xl font-extrabold text-neutral-800'>
                    Crear formulario
                </h1>
                <div className='flex w-full flex-col gap-4 rounded-md bg-white p-8 shadow-md'>
                    {INPUT_FIELDS.map((field, idx) => {
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
                            onClick={handleCreateForm}
                        />
                    </div>
                </div>
            </section>
        </Layout>
    )
}

export default CreateForm