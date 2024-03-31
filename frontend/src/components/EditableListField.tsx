'use client'

import {ChangeEvent, useEffect, useState} from 'react'
import {MdEditSquare} from 'react-icons/md'
import {MdAddCircle, MdCancel} from 'react-icons/md'
import {MdDelete} from 'react-icons/md'
import IconButton from './IconButton'

interface EditableListFieldProps {
    editable?: boolean
    setListValues: (listValues: string[]) => void
    listValues: string[]
    label?: string
    editableOnly?: boolean
    souldForceReset?: boolean
}

const EditableListField = ({
    setListValues,
    listValues,
    label,
    editableOnly,
    souldForceReset,
}: EditableListFieldProps) => {
    const [isEditing, setIsEditing] = useState<boolean>(false)
    const originalValues = [...listValues]

    const handleEditField = () => {
        setIsEditing(true)
    }

    const handleFieldChange = (
        e: ChangeEvent<HTMLInputElement>,
        idx: number
    ) => {
        const newValues = listValues.map((field: string, subIdx: number) => {
            if (subIdx === idx) {
                return e.target.value
            }
            return field
        })
        setListValues(newValues)
    }

    const handleAddSubField = () => {
        setListValues([...listValues, ''])
    }

    const handleRemoveField = (idx: number) => {
        if (listValues.length > 1) {
            const newValues = listValues.filter((_, subIdx) => idx !== subIdx)
            setListValues(newValues)
        }
    }

    const handleReset = () => {
        setIsEditing(false)
        setListValues(originalValues)
    }

    useEffect(() => {
        if (souldForceReset) {
            setIsEditing(false)
        }
    }, [souldForceReset])

    return (
        <div className='mb-1'>
            <div className='flex flex-row items-center gap-2'>
                {label && (
                    <h2 className='text-lg font-semibold capitalize text-slate-800'>
                        {label}
                    </h2>
                )}
                {isEditing || editableOnly ? (
                    <div className='flex flex-row items-center gap-2'>
                        <IconButton
                            onClick={handleAddSubField}
                            Icon={MdAddCircle}
                            size='text-lg'
                        />
                        {!editableOnly && (
                            <IconButton
                                Icon={MdCancel}
                                onClick={handleReset}
                                size='text-lg'
                            />
                        )}
                    </div>
                ) : (
                    <IconButton
                        onClick={handleEditField}
                        Icon={MdEditSquare}
                        size='text-lg'
                    />
                )}
            </div>
            <div className='flex w-full flex-col gap-2'>
                {listValues?.map((value: string, idx: number) => {
                    return isEditing || editableOnly ? (
                        <div
                            key={idx}
                            className='flex w-full max-w-full flex-row items-center gap-2'>
                            <input
                                className='my-2  flex-grow rounded-md border-2 border-gray-300 px-1 text-slate-500'
                                onChange={(e) => handleFieldChange(e, idx)}
                                value={value}
                            />
                            {listValues.length > 1 && idx > 0 && (
                                <div className='shrink-0'>
                                    <IconButton
                                        onClick={() => handleRemoveField(idx)}
                                        Icon={MdDelete}
                                        size='text-lg'
                                        fill='text-red-500'
                                    />
                                </div>
                            )}
                        </div>
                    ) : (
                        <p key={idx}>{value}</p>
                    )
                })}
            </div>
        </div>
    )
}

export default EditableListField
