'use client'
import Layout from '@/components/layout'
import useGetForms from '@/hooks/useGetForms'
import React, {useEffect, useMemo, useState} from 'react'
import {MdEdit} from 'react-icons/md'
import {Form, FormKeys} from '@/types/Forms'
import useEditForm from '@/hooks/useEditForm'
import EditableInputField from '@/components/EditableInputField'
import EditableListField from '@/components/EditableListField'

const VISIBLE_FIELDS = ['automatic_response_id', 'examples', 'name', 'response']

const FormDetail = ({params}: {params: {'automatic-response-id': string}}) => {
    const {'automatic-response-id': formId} = params
    const {data, isLoading} = useGetForms(formId)
    const [isEditingForm, setIsEditingForm] = useState<boolean>(false)
    const [editedForm, setEditedForm] = useState<any>()
    const {
        submit,
        isLoading: isUpdateLoading,
        error,
    } = useEditForm(formId, editedForm as Form)
    const formFields = useMemo(() => {
        if (data && data?.automatic_response) {
            const filteredFormFields = Object.keys(
                data.automatic_response
            ).filter((fieldName: string) => VISIBLE_FIELDS.includes(fieldName))

            const filteredData = filteredFormFields.reduce((acc, curr) => {
                acc[curr] = data.automatic_response[curr]
                return acc
            }, {})

            return filteredData
        }
        return []
    }, [data])

    useEffect(() => {
        if (data) {
            setEditedForm({...formFields})
        }
    }, [data, formFields])

    return (
        <Layout>
            <section className='flex flex-col'>
                <h1 className='mb-4 text-3xl font-extrabold text-slate-800'>
                    Detalles de formulario
                </h1>
                <div className='w-full rounded-md bg-white p-8 shadow-md'>
                    {Object.keys(formFields).map(
                        (field: string, idx: number) => {
                            if (typeof formFields[field] === 'string') {
                                return (
                                    <EditableInputField
                                        editedForm={editedForm}
                                        setEditedForm={setEditedForm}
                                        editable={
                                            field !== 'automatic_response_id'
                                        }
                                        isEditingForm={isEditingForm}
                                        fieldName={field}
                                        fieldValue={formFields[field] || ''}
                                        key={idx}
                                        setIsEditingForm={setIsEditingForm}
                                    />
                                )
                            }

                            return (
                                <EditableListField
                                    editedForm={editedForm}
                                    setEditedForm={setEditedForm}
                                    editable={field !== 'automatic_response_id'}
                                    isEditingForm={isEditingForm}
                                    key={idx}
                                    fieldName={field}
                                    fieldValue={formFields[field] || []}
                                    setIsEditingForm={setIsEditingForm}
                                />
                            )
                        }
                    )}
                    {isEditingForm && (
                        <div className='flex w-full flex-row items-center justify-end gap-2'>
                            <button>Descartar</button>
                            <button
                                className='disabled:text-gray-300'
                                onClick={async () => await submit()}>
                                Guardar
                            </button>
                        </div>
                    )}
                </div>
            </section>
        </Layout>
    )
}

export default FormDetail
