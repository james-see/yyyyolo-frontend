from django.core.checks.messages import Error
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from .models import Prank, Like
from django.db.models import Q
from users.schema import UserType


class PrankType(DjangoObjectType):
    class Meta:
        model = Prank


class LikeType(DjangoObjectType):
    class Meta:
        model = Like


class Query(graphene.ObjectType):
    pranks = graphene.List(PrankType, search=graphene.String())
    likes = graphene.List(LikeType)

    def resolve_pranks(self, info, search=None):
        if search:
            filter = (
                Q(title__icontains=search) |
                Q(description__icontains=search)|
                Q(url__icontains=search)|
                Q(posted_by__username__icontains=search)
            )
            return Prank.objects.filter(filter)
        return Prank.objects.all()

    def resolve_likes(self, info):
        return Like. objects.all()


class CreatePrank(graphene.Mutation):
    prank = graphene.Field(PrankType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, title, description, url):
        user = info.context.user or None

        if user.is_anonymous:
            raise GraphQLError('Log in to add a prank.')

        prank = Prank(title=title, description=description, url=url, posted_by=user)
        prank.save()
        return CreatePrank(prank=prank)


class UpdatePrank(graphene.Mutation):
    prank = graphene.Field(PrankType)

    class Arguments:
        prank_id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()
    
    def mutate(self, info, prank_id, title, url, description):

        user = info.context.user
        prank = Prank.objects.get(id=prank_id)

        if prank.posted_by != user:
            raise GraphQLError('Not permitted to update this track.')

        prank.title = title
        prank.description = description
        prank.url = url
        prank.save()

        return UpdatePrank(prank=prank)


class DeletePrank(graphene.Mutation):
    prank_id = graphene.Int()

    class Arguments:
        prank_id = graphene.Int(required=True)

    def mutate(self, info, prank_id):
        user = info.context.user
        prank = Prank.objects.get(id=prank_id)

        if prank.posted_by != user:
            raise GraphQLError('Not permitted to delete this track.')

        prank.delete()

        return DeletePrank(prank_id=prank_id)


class CreateLike(graphene.Mutation):
    user = graphene.Field(UserType)
    prank = graphene.Field(PrankType)

    class Arguments:
        prank_id = graphene.Int(required=True)
    
    def mutate(self, info, prank_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login to like tracks.')

        prank = Prank.objects.get(id=prank_id)
        if not prank:
            raise GraphQLError('Cannot find track with given id')

        Like.objects.create(user=user, prank=prank)
        
        return CreateLike(user, prank)

class Mutation(graphene.ObjectType):
    create_prank = CreatePrank.Field()
    update_prank = UpdatePrank.Field()
    delete_prank = DeletePrank.Field()
    create_like = CreateLike.Field()