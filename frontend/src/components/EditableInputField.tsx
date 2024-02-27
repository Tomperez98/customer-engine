'use client'

import React, {useState} from 'react'
import {MdEdit} from 'react-icons/md'
import {FormKeys} from '@/types/Forms'

interface EditableInputFieldProps {
    fieldName: string
    fieldValue: string
    isEditingForm: boolean
    setIsEditingForm: (isEditingForm: boolean) => void
    editable?: boolean
    setEditedForm: any
    editedForm: any
}

const EditableInputField = ({
    fieldName,
    fieldValue,
    editable,
    isEditingForm,
    setIsEditingForm,
    setEditedForm,
    editedForm,
}: EditableInputFieldProps) => {
    const [isEditing, setIsEditing] = useState<boolean>(false)

    const handleEditField = () => {
        if (!isEditingForm) {
            setIsEditingForm(true)
        }
        setIsEditing(true)
    }

    const handleInputFieldChange = (event: any) => {
        setEditedForm({...editedForm, [fieldName]: event.target.value})
    }
    return (
        <div className='mb-1'>
            <div className='flex flex-row items-center gap-2'>
                <h2 className='text-lg font-extrabold capitalize text-slate-800'>
                    {FormKeys[fieldName as keyof typeof FormKeys] || fieldName}
                </h2>
                {!isEditing && editable && (
                    <MdEdit
                        className='cursor-pointer'
                        onClick={handleEditField}
                    />
                )}
            </div>
            {isEditing && editable ? (
                <input
                    className='rounded-md border-2 border-gray-300 px-1 text-slate-500'
                    onChange={handleInputFieldChange}
                    value={editedForm[fieldName]}
                />
            ) : (
                <p>{fieldValue}</p>
            )}
        </div>
    )
}

export default EditableInputField
