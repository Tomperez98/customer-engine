'use-client'
import useGetForms from '@/hooks/forms/useGetForms'
import React, {useEffect, useMemo, useState} from 'react'
import {Form, FormKey, FormKeys, FormTemplate} from '@/types/Forms'
import useEditForm from '@/hooks/forms/useEditForm'
import EditableInputField from '@/components/EditableInputField'
import {FORM_TEMPLATE, FORM_FIELDS} from '@/constants/formFields'
import {
    validateFormHasChanges,
    validateNoEmptyFields,
} from '@/utils/validateFormFields'
import Button from '@/components/Button'

interface FormDetailsSectionProps {
    formId: string
}

const FormDetailsSection = ({formId}: FormDetailsSectionProps) => {
    const {data, isLoading, refetch} = useGetForms(formId)
    const [resetAllFormFields, setResetAllFormFields] = useState<boolean>(false)
    const [shouldRefetch, setShouldRefetch] = useState<boolean>(false)
    const [isEditingForm, setIsEditingForm] = useState<boolean>(false)
    const [editFormTemplate, setEditFormTemplate] =
        useState<FormTemplate>(FORM_TEMPLATE)
    const {
        submit,
        isLoading: isUpdateLoading,
        error,
    } = useEditForm(formId, editFormTemplate as Form)

    const formData = useMemo(() => data?.automatic_response as Form, [data])

    const relevantData = useMemo(() => {
        return Object.keys(FORM_TEMPLATE).reduce(
            (acc, key) => {
                if (data?.automatic_response?.hasOwnProperty(key)) {
                    acc[key] = formData[key as FormKey]
                }
                return acc
            },
            {} as {[key: string]: string | string[]}
        )
    }, [data, formData])

    const areChangesValid =
        validateNoEmptyFields(editFormTemplate) &&
        validateFormHasChanges(editFormTemplate, relevantData as FormTemplate)

    const handleSaveChanges = async () => {
        await submit()
        setShouldRefetch(true)
        setResetAllFormFields(true)
    }

    const handleRefetch = () => {
        refetch()
        setResetAllFormFields(false)
        setIsEditingForm(false)
        setShouldRefetch(false)
    }

    useEffect(() => {
        if (data) {
            setEditFormTemplate({...(relevantData as FormTemplate)})
        }
    }, [data, relevantData])

    useEffect(() => {
        if (shouldRefetch) {
            handleRefetch()
        }
    }, [shouldRefetch])

    return (
        <section className='flex flex-col'>
            <h1 className='mb-4 text-3xl font-extrabold text-slate-800'>
                Detalles de formulario
            </h1>
            <div className='w-full rounded-md bg-white p-8 shadow-md'>
                {formData && (
                    <div className='flex flex-col gap-2'>
                        <>
                            <label
                                htmlFor='automatic_response_id'
                                className='text-lg font-semibold capitalize text-neutral-800'>
                                {FormKeys['automatic_response_id']}
                            </label>
                            <p>{formData?.automatic_response_id}</p>
                        </>
                        {FORM_FIELDS.map((field, idx: number) => {
                            return (
                                <EditableInputField
                                    fieldName={field.name as FormKey}
                                    template={editFormTemplate}
                                    isEditingTemplate={isEditingForm}
                                    key={idx}
                                    label={field.label}
                                    originalValue={
                                        formData[field?.name as FormKey]
                                    }
                                    setTemplate={setEditFormTemplate}
                                    setIsEditingTemplate={setIsEditingForm}
                                    souldForceReset={resetAllFormFields}
                                    type={
                                        field.component as 'input' | 'textarea'
                                    }
                                />
                            )
                        })}
                    </div>
                )}
                {isEditingForm && (
                    <div className='mt-4 flex w-full flex-row items-center justify-end gap-4'>
                        <Button
                            disabled={!areChangesValid}
                            onClick={handleSaveChanges}
                            label='Guardar'
                        />
                    </div>
                )}
            </div>
        </section>
    )
}

export default FormDetailsSection
