import Modal from './Modal'
import Button from '../Button'

interface DeleteConfirmationModalProps {
    deleteAction: () => void
    elementName: string
    isOpen: boolean
    setIsOpen: (isOpen: boolean) => void
}

const DeleteConfirmationModal = ({
    deleteAction,
    elementName,
    isOpen,
    setIsOpen,
}: DeleteConfirmationModalProps) => {
    return (
        <Modal isOpen={isOpen} setIsOpen={setIsOpen}>
            <div className='flex flex-col gap-2'>
                <h3 className='mt-2 text-2xl font-extrabold text-neutral-800'>
                    ¡Atención! Estás a punto de borrar un {elementName}.
                </h3>
                <p>
                    Esta acción es permanente y no podrá deshacerse una vez
                    confirmada.
                </p>
                <p>¿Deseas proceder con la eliminación?</p>
                <div className='flex w-full justify-end'>
                    <Button
                        label={`Eliminar ${elementName}`}
                        onClick={deleteAction}
                    />
                </div>
            </div>
        </Modal>
    )
}

export default DeleteConfirmationModal
