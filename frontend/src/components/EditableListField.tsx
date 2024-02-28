'use client'

import {useState} from 'react'
import {MdEdit} from 'react-icons/md'

interface EditableListFieldProps {
    fieldName: string
    isEditingForm: boolean
    setIsEditingForm: (isEditingForm: boolean) => void
    editable?: boolean
    setEditedForm: any
    editedForm: any
    originalValue: any
    label: string
}

const EditableListField = ({
    fieldName,
    isEditingForm,
    setIsEditingForm,
    setEditedForm,
    editedForm,
    originalValue,
    label,
}: EditableListFieldProps) => {
    const [isEditing, setIsEditing] = useState<boolean>(false)

    const handleEditField = () => {
        if (!isEditingForm) {
            setIsEditingForm(true)
        }
        setIsEditing(true)
    }

    const handleSubFieldChange = (e: any, idx: number) => {
        setEditedForm({
            ...editedForm,
            [fieldName]: editedForm[fieldName].map(
                (field: any, subIdx: number) => {
                    if (subIdx === idx) {
                        return e.target.value
                    }
                    return field
                }
            ),
        })
    }

    const handleAddSubField = () => {
        setEditedForm({
            ...editedForm,
            [fieldName]: [...editedForm[fieldName], ''],
        })
    }

    const handleRemoveSubField = (value: string) => {
        if (editedForm[fieldName].length > 1) {
            setEditedForm({
                ...editedForm,
                [fieldName]: editedForm[fieldName].filter(
                    (field: any) => field !== value
                ),
            })
        }
    }

    const handleReset = () => {
        setIsEditing(false)
        setEditedForm({...editedForm, [fieldName]: originalValue})
    }

    return (
        <div className='mb-1'>
            <div className='flex flex-row items-center gap-2'>
                <h2 className='text-lg font-extrabold capitalize text-slate-800'>
                    {label}
                </h2>
                {isEditing ? (
                    <div className='flex flex-row gap-2'>
                        <button onClick={handleAddSubField}>add</button>
                        <button onClick={handleReset}>reset</button>
                    </div>
                ) : (
                    <MdEdit
                        className='cursor-pointer'
                        onClick={handleEditField}
                    />
                )}
            </div>
            <div className='flex flex-col gap-2'>
                {editedForm?.[fieldName].map((field: any, idx: number) => {
                    return isEditing ? (
                        <div key={idx}>
                            <input
                                className='mr-2 rounded-md border-2 border-gray-300 px-1 text-slate-500'
                                onChange={(e) => handleSubFieldChange(e, idx)}
                                value={editedForm[fieldName][idx]}
                            />
                            <button onClick={() => handleRemoveSubField(field)}>
                                delete
                            </button>
                        </div>
                    ) : (
                        <p key={idx}>{field}</p>
                    )
                })}
            </div>
        </div>
    )
}

export default EditableListField
